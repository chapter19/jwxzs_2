#-*- coding:utf-8 -*-

from rest_framework import serializers

from spiders.subject_system import Pingjiao
from utils.aes import return_my_words
from users.models import MyPassword,UserProfile
import json

from .models import PingJiaoTeacher
from .tasks import pingjiao_list_create_pingjiaoteacher,update_pingjiao
from semesters.models import CurrentSemester
from users.models import Teacher

from .models import MyXuanKe,StepOneLessonTeacher
from lessons.serializer import LessonSerializers
from users.serializer import TeacherSerializer

from spiders.subject_system import XuanKe


# class TeacherSerializer(serializers.ModelSerializer):
#     class Meta:
#         model=Teacher
#         fields='__all__'

class PingJiaoListSerializer(serializers.Serializer):
    user_id = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    def create(self, validated_data):
        user_id=validated_data.get('user_id')
        current_semester=CurrentSemester.objects.first().current_semester
        pjt=PingJiaoTeacher.objects.filter(semester=current_semester,student__user_id=user_id)
        if not pjt:
            user = UserProfile.objects.get(id=user_id)
            # student_id=validated_data.get('student_id')
            my_password=MyPassword.objects.get(user=user)
            password=return_my_words(my_password.password)
            pingjiao=Pingjiao(student_id=user.student.id,student_password=password)
            pingjiao.login()
            data=pingjiao.get_my_pingjiao()
            # data=json.dumps(data)
            if data:
                pingjiao_list_create_pingjiaoteacher.delay(user.username,data)
                return data
            else:
                raise serializers.ValidationError({'detail':'获取评教失败，请稍后重试'})
        else:
            lis= pjt.values('lesson_name','teacher','semester','code')
            i=0
            for li in lis:
                teacher=Teacher.objects.get(id=li['teacher'])
                lis[i]['teacher']={'id':teacher.id,'name':teacher.name}
                i+=1
            return lis




class PingJiaoCreateSerializer(serializers.Serializer):
    user_id = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    groupA=serializers.CharField(required=False,write_only=True,help_text='等级优秀的老师，格式: 267211K003550BJH3|262064K004626BJH2|',label='等级优秀',default='')
    groupB=serializers.CharField(required=False,write_only=True,help_text='等级良好的老师，格式: 同groupA',label='等级良好',default='')
    groupC=serializers.CharField(required=False,write_only=True,help_text='等级中等的老师，格式: 同groupA',label='等级中等',default='')
    groupD=serializers.CharField(required=False,write_only=True,help_text='等级合格的老师，格式: 同groupA',label='等级合格',default='')
    def create(self, validated_data):
        user_id = validated_data.get('user_id')
        groupA=validated_data.get('groupA')
        groupB=validated_data.get('groupB')
        groupC=validated_data.get('groupC')
        groupD=validated_data.get('groupD')
        current_semester = CurrentSemester.objects.first().current_semester
        pjt = PingJiaoTeacher.objects.filter(semester=current_semester, student__user_id=user_id)
        if pjt:
            if groupA:
                liA=groupA.split('|')[:-1]
                print(liA)
                if 2*len(liA)>pjt.count():
                    raise serializers.ValidationError({'detail':'优秀老师不能大于50%！'})
                else:
                    user = UserProfile.objects.get(id=user_id)
                    my_password = MyPassword.objects.get(user=user)
                    password = return_my_words(my_password.password)
                    pingjiao = Pingjiao(student_id=user.student.id, student_password=password)
                    pingjiao.login()
                    data=pingjiao.pingjiao(groupA,groupB,groupC,groupD)
                    for a in liA:
                        pjt.filter(code=a).update(grade='groupA')
                    if groupB:
                        liB = groupB.split('|')[:-1]
                        for b in liB:
                            pjt.filter(code=b).update(grade='groupB')
                    if groupC:
                        liC = groupC.split('|')[:-1]
                        for c in liC:
                            pjt.filter(code=c).update(grade='groupC')
                    if groupD:
                        liD = groupD.split('|')[:-1]
                        for d in liD:
                            pjt.filter(code=d).update(grade='groupD')
                    # update_pingjiao.delay(pjt, liA, groupB, groupC, groupD)
                    return data
            else:
                user = UserProfile.objects.get(id=user_id)
                my_password = MyPassword.objects.get(user=user)
                password = return_my_words(my_password.password)
                pingjiao = Pingjiao(student_id=user.student.id, student_password=password)
                pingjiao.login()
                data = pingjiao.pingjiao(groupA, groupB, groupC, groupD)
                if groupB:
                    liB = groupB.split('|')[:-1]
                    for b in liB:
                        pjt.filter(code=b).update(grade='groupB')
                if groupC:
                    liC = groupC.split('|')[:-1]
                    for c in liC:
                        pjt.filter(code=c).update(grade='groupC')
                if groupD:
                    liD = groupD.split('|')[:-1]
                    for d in liD:
                        pjt.filter(code=d).update(grade='groupD')
                # update_pingjiao.delay(pjt,'', groupB, groupC, groupD)
                return data
        else:
            raise serializers.ValidationError({'detail':'请先查看评教列表！'})



class StepOneLessonTeacherSerializer(serializers.ModelSerializer):
    lesson=LessonSerializers()
    teacher=TeacherSerializer()
    class Meta:
        model=StepOneLessonTeacher
        fields=['lesson','teacher','semester','post_code']


class XuankeListSerializers(serializers.ModelSerializer):
    lesson_teacher=StepOneLessonTeacherSerializer()
    class Meta:
        model=MyXuanKe
        fields=['lesson_type','lesson_teacher','point','delete_post_code']


class SynchronizeXuankeSerializer(serializers.Serializer):
    user_id=serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    def create(self, validated_data):
        try:
            user_id=validated_data.get('user_id')
            user=UserProfile.objects.get(id=user_id)
            my_password = MyPassword.objects.get(user=user)
            password = return_my_words(my_password.password)
            xuanke=XuanKe(student_id=user.student.id, student_password=password)
            xuanke.login()
            xuanke.clean_xuanke_page()
            xuanke.get_xuanke_page()
            return {'detail':'同步成功'}
        except:
            return {'detail':'同步失败，可能你的本站密码和教务在线（选课系统）密码不一致，请先同步密码！'}


class DeleteXuankeSerializer(serializers.Serializer):
    user_id = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    kch=serializers.CharField(write_only=True,required=True,help_text='课程号',label='课程号',max_length=8,min_length=4)
    def create(self, validated_data):
        try:
            kch=validated_data.get('kch')
            user_id = validated_data.get('user_id')
            user = UserProfile.objects.get(id=user_id)
            my_password = MyPassword.objects.get(user=user)
            password = return_my_words(my_password.password)
            xuanke = XuanKe(student_id=user.student.id, student_password=password)
            xuanke.login()
            d=xuanke.delete_lesson(kch)
            if d:
                return {'detail':'删除成功！'}
            else:
                return {'detail':'该课程不允许删除！'}
        except:
            return {'detail': '删除失败，可能你的本站密码和教务在线（选课系统）密码不一致，请先同步密码！'}


class SetXuanDianSerializer(serializers.Serializer):
    user_id = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    kch = serializers.CharField(write_only=True, required=True, help_text='课程号', label='课程号',max_length=8,min_length=4)
    xd=serializers.IntegerField(write_only=True,required=True,help_text='选点',label='选点')
    def create(self, validated_data):
        try:
            kch=validated_data.get('kch')
            xd=validated_data.get('xd')
            user_id = validated_data.get('user_id')
            user = UserProfile.objects.get(id=user_id)
            my_password = MyPassword.objects.get(user=user)
            password = return_my_words(my_password.password)
            xuanke = XuanKe(student_id=user.student.id, student_password=password)
            xuanke.login()
            set_xd=xuanke.set_xuandian(kch=kch,xd=xd)
            if set_xd:
                return {'detail':'选点设置成功！'}
            else:
                return {'detail':'设置失败！你可能没有选择该课程，或该课程无需设置选点，或者超出最大选点！'}
        except:
            return {'detail':'设置失败，可能你的本站密码和教务在线（选课系统）密码不一致，请先同步密码！'}



class XuanKeSerializer(serializers.Serializer):
    user_id = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    kch = serializers.CharField(write_only=True, required=True, help_text='课程号', label='课程号', max_length=8,min_length=4)
    post_data=serializers.CharField(write_only=True,required=True,help_text='选择老师的表单码',label='选择老师的表单码')
    teacher_id=serializers.CharField(write_only=True,required=True,help_text='教师号',label='教师号')
    def create(self, validated_data):
        try:
            kch = validated_data.get('kch')
            teacher_id = validated_data.get('teacher_id')
            post_data = validated_data.get('post_data')
            solt=StepOneLessonTeacher.objects.filter(teacher_id=teacher_id,post_code=post_data)
            if solt:
                user_id = validated_data.get('user_id')
                user = UserProfile.objects.get(id=user_id)
                my_password = MyPassword.objects.get(user=user)
                password = return_my_words(my_password.password)
                xuanke = XuanKe(student_id=user.student.id, student_password=password)
                xuanke.login()
                xk=xuanke.xuanke(kch=kch,post_data=post_data,teacher_id=teacher_id)
                if xk:
                    return {'detail':'选课成功！'}
                else:
                    return {'detail':'选课失败！你不能选择该课程'}
            else:
                return {'detail':'你的表单码和教师不一致！'}
        except:
            return {'detail': '选课失败，可能你的本站密码和教务在线（选课系统）密码不一致，请先同步密码！'}

