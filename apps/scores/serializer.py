#-*- coding:utf-8 -*-

from rest_framework import serializers
from .models import Score,TotalCredit,NewScore
from users.serializer import TeacherSerializer,StudentSerializer
from lessons.serializer import LessonSerializers,ScheduleLessonSerializers
from spiders.student_dynamic import SpiderDynamicStudent
from users.models import MyPassword,UserProfile
from utils.aes import return_my_words

from .tasks import update_score
from semesters.models import Semester


class ScoreSerializer(serializers.ModelSerializer):
    # student=StudentSerializer()
    qinghua_data = serializers.SerializerMethodField()
    def get_qinghua_data(self, obj):
        if obj.score >= 100:
            qinghua_data = {
                'grade': 'A+',
                'grade_point': 4.0,
                'evaluation': '优秀',
                'credit_score': 4.0 * obj.schedule_lesson.lesson.credit
            }
        elif obj.score >= 95:
            qinghua_data = {
                'grade': 'A',
                'grade_point': 4.0,
                'evaluation': '优秀',
                'credit_score': 4.0 * obj.schedule_lesson.lesson.credit
            }
        elif obj.score >= 90:
            qinghua_data = {
                'grade': 'A-',
                'grade_point': 3.7,
                'evaluation': '优秀',
                'credit_score': 3.7 * obj.schedule_lesson.lesson.credit
            }
        elif obj.score >= 85:
            qinghua_data = {
                'grade': 'B+',
                'grade_point': 3.3,
                'evaluation': '良好',
                'credit_score': 3.3 * obj.schedule_lesson.lesson.credit
            }
        elif obj.score >= 80:
            qinghua_data = {
                'grade': 'B',
                'grade_point': 3.0,
                'evaluation': '良好',
                'credit_score': 3.0 * obj.schedule_lesson.lesson.credit
            }
        elif obj.score >= 77:
            qinghua_data = {
                'grade': 'B-',
                'grade_point': 2.7,
                'evaluation': '良好',
                'credit_score': 2.7 * obj.schedule_lesson.lesson.credit
            }
        elif obj.score >= 73:
            qinghua_data = {
                'grade': 'C+',
                'grade_point': 2.3,
                'evaluation': '一般',
                # 'credit_score': 2.3 * obj.schedule_lesson.lesson.credit
                'credit_score': 2.3 * obj.schedule_lesson.lesson.credit
            }
        elif obj.score >= 70:
            qinghua_data = {
                'grade': 'C',
                'grade_point': 2.0,
                'evaluation': '一般',
                'credit_score': 2.0 * obj.schedule_lesson.lesson.credit
            }
        elif obj.score >= 67:
            qinghua_data = {
                'grade': 'C-',
                'grade_point': 1.7,
                'evaluation': '一般',
                'credit_score': 1.7 * obj.schedule_lesson.lesson.credit
            }
        elif obj.score >= 63:
            qinghua_data = {
                'grade': 'D+',
                'grade_point': 1.3,
                'evaluation': '及格',
                'credit_score': 1.3 * obj.schedule_lesson.lesson.credit
            }
        elif obj.score >= 60:
            qinghua_data = {
                'grade': 'D',
                'grade_point': 1.0,
                'evaluation': '及格',
                'credit_score': 1.0 * obj.schedule_lesson.lesson.credit
            }
        else:
            qinghua_data = {
                'grade': 'F',
                'grade_point': 0.0,
                'evaluation': '不及格',
                'credit_score': 0.0
            }
        return qinghua_data
    schedule_lesson=ScheduleLessonSerializers()
    class Meta:
        model=Score
        fields='__all__'


class ScoreStudentListSerializer(serializers.ModelSerializer):
    student=StudentSerializer()
    class Meta:
        model=Score
        fields=['student',]


class TotalCreditSerializer(serializers.ModelSerializer):
    # student = StudentSerializer()
    # student__id =serializers.SerializerMethodField(label='学号')
    class Meta:
        model=TotalCredit
        fields=('credit','standard_score',)

    # def get_student__id(self,obj):
    #     return obj.username


class ScoreSemesterSerializer(serializers.Serializer):
    student_id=serializers.CharField(max_length=12,min_length=10,help_text='学号',label='学号',required=True,write_only=True)
    def create(self, validated_data):
        student_id=validated_data.get('student_id')
        list = Score.objects.filter(student_id=student_id).values('schedule_lesson__semester').distinct().order_by('-schedule_lesson__semester')
        retu_list = []
        for li in list:
            semester = Semester.objects.filter(post_code=li['schedule_lesson__semester']).values('post_code', 'verbose_name')[0]
            retu_list.append(semester)
        return retu_list


class ScoreUpdateSerializer(serializers.Serializer):
    user_id = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    def create(self, validated_data):
        user_id=validated_data.get('user_id')
        user=UserProfile.objects.get(id=user_id)
        if not user.is_active:
            raise serializers.ValidationError({'detail': '你的账号不能再继续使用'})
        if user.is_student:
            my_password=MyPassword.objects.filter(user_id=user_id)
            if my_password:
                my_password=my_password[0]
                word=return_my_words(my_password.password)
                spd=SpiderDynamicStudent(user.username,word)
                login=spd.sign_in()
                if login:
                    update_score.delay(user.username,word)
                    return {'detail':'更新成绩单成功'}
                else:
                    return {'detail':'你的本站密码与教务在线密码不一致，需要先同步密码！'}
            else:
                return {'detail':'系统异常，未保存你的教务在线密码'}
        else:
            return {'detail':'你不是学生，不能更新成绩！'}


class NewScoreListSerializer(serializers.ModelSerializer):
    class Meta:
        model=NewScore
        fields='__all__'

class NewScoreUpdateSerializer(serializers.Serializer):
    user_id = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    def create(self, validated_data):
        user_id=validated_data.get('user_id')
        user=UserProfile.objects.get(id=user_id)
        if not user.is_active:
            raise serializers.ValidationError({'detail': '你的账号不能再继续使用'})
        if user.is_student:
            my_password = MyPassword.objects.filter(user_id=user_id)
            if my_password:
                my_password = my_password[0]
                word = return_my_words(my_password.password)
                spd = SpiderDynamicStudent(user.username, word)
                login = spd.sign_in()
                if login:
                    NewScore.objects.filter(student_id=user.username).delete()
                    spd.get_new_score()
                    return {'detail': '更新成绩单成功'}
                else:
                    return {'detail': '你的本站密码与教务在线密码不一致，需要先同步密码！'}
            else:
                return {'detail': '系统异常，未保存你的教务在线密码'}
        else:
            return {'detail': '你不是学生，不能更新成绩！'}
