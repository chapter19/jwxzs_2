#-*- coding:utf-8 -*-
from rest_framework import serializers
from datetime import datetime
from datetime import timedelta

from .models import TheCheck,CheckedStudent,ScheduleLesson
from groups.models import Group
from lessons.serializer import ScheduleLessonSerializers
from users.models import UserProfile,Student
from users.serializer import StudentSerializer


class TheCheckViewCreateSerializer(serializers.Serializer):
    promoter= serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    schedule_lesson_id=serializers.IntegerField(min_value=0,required=True,label='课程表课程班级',help_text='课程表课程班级')
    time_limit=serializers.IntegerField(min_value=1,max_value=120,default=3,required=False,label='过期时间/分钟',help_text='过期时间/分钟')
    password=serializers.IntegerField(min_value=123,required=False,label='点到密码',help_text='点到密码',default=None)
    def create(self, validated_data):
        promoter=validated_data.get('promoter')
        schedule_lesson_id=validated_data.get('schedule_lesson_id')
        group=Group.objects.filter(group_type=1,group_id=str(schedule_lesson_id),group_admin__admin_id=promoter)
        if group:
            now = datetime.now()
            one_minute_ago = now-timedelta(hours=0, minutes=1, seconds=0)
            one_minute_last_check=TheCheck.objects.filter(schedule_lesson_id=schedule_lesson_id,start_time__gt=one_minute_ago)
            if not one_minute_last_check:
                time_limit = validated_data.get('time_limit')
                password = validated_data.get('password')
                the_check=TheCheck.objects.create(promoter_id=promoter,schedule_lesson_id=schedule_lesson_id,time_limit=time_limit,password=password)
                stus=UserProfile.objects.filter(student__score__schedule_lesson_id=schedule_lesson_id)
                for st in stus:
                    CheckedStudent.objects.create(the_check=the_check,student=st)
                return the_check
            else:
                raise serializers.ValidationError({'detail':'你在一分钟内已向该课程班级发起过点到，请先确认你的需求。若有需要，你可以重新编辑该点到，或者先删除上一次点到再重新创建！'})
        else:
            raise serializers.ValidationError({'detail':'你不是该课程班级的管理员，没有权限向该课程班级发起点到！'})
    class Meta:
        model=TheCheck
        fields=['promoter','schedule_lesson','password','time_limit']


class TheCheckViewSerializer(serializers.ModelSerializer):
    schedule_lesson=ScheduleLessonSerializers()
    class Meta:
        model=TheCheck
        fields=['promoter','schedule_lesson','start_time','time_limit','id']



class TheCheckViewUpdateSerializer(serializers.Serializer):
    user= serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    more_minute=serializers.IntegerField(min_value=1,max_value=120,default=3,required=False,label='再给几分钟',help_text='再给几分钟',write_only=True)
    password=serializers.IntegerField(min_value=123,required=False,label='点到密码',help_text='点到密码')
    def update(self, instance, validated_data):
        user = validated_data.get('user')
        schedule_lesson=instance.schedule_lesson
        group = Group.objects.filter(group_type=1, group_id=str(schedule_lesson.id), group_admin__admin_id=user)
        if group:
            more_minute=validated_data.get('more_minute')
            password=validated_data.get('password')
            if more_minute:
                minute_ago=datetime.now()-timedelta(hours=0,minutes=instance.time_limit,seconds=0)
                if instance.start_time<minute_ago:
                    #若过期了，则从现在开始加几分钟
                    instance.time_limit=int((datetime.now()-instance.start_time).seconds/60)+more_minute
                else:
                    #若没过期，则再原来的基础上加几分钟
                    instance.time_limit=instance.time_limit+more_minute
            if password:
                instance.password=password
            instance.save()
            return instance
        else:
            raise serializers.ValidationError({'detail':'你不是该课程班级的管理员，没有权限向该课程班级发起点到！'})
    class Meta:
        model=TheCheck
        fields=['user','more_minute','password']



class StudentCheckedStudentListSerializer(serializers.ModelSerializer):
    the_check=TheCheckViewSerializer()
    class Meta:
        model=CheckedStudent
        fields=['check_time','the_check','id']


class UserProfileSerializer(serializers.ModelSerializer):
    student=StudentSerializer()
    class Meta:
        model=UserProfile
        fields=['id','student']


class TeacherCheckedStudentListSerializer(serializers.ModelSerializer):
    student=UserProfileSerializer()
    class Meta:
        model=CheckedStudent
        fields=['check_time','student','id']


class StudentCheckedStudentUpdateSerializer(serializers.Serializer):
    def update(self, instance, validated_data):
        if not instance.check_time:
            over_time=instance.the_check.start_time+timedelta(hours=0,minutes=instance.time_limit,seconds=0)
            now_time=datetime.now()
            if over_time>now_time:
                instance.check_time=now_time
                instance.save()
                return instance
            else:
                raise serializers.ValidationError({'detail':'已超过点到时间！'})
        else:
            raise serializers.ValidationError({'detail':'你已经点到过了，请勿重复点到！'})
    class Meta:
        model=CheckedStudent
        fields=[]






