#-*- coding:utf-8 -*-

from rest_framework import serializers
from .models import Score,TotalCredit
from users.serializer import TeacherSerializer,StudentSerializer
from lessons.serializer import LessonSerializers,ScheduleLessonSerializers


class ScoreSerializer(serializers.ModelSerializer):
    # student=StudentSerializer()
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









