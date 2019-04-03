#-*- coding:utf-8 -*-
from rest_framework import serializers
from .models import Schedule,ScheduleLesson,Lesson
from users.serializer import TeacherSerializer


class LessonSerializers(serializers.ModelSerializer):
    class Meta:
        model=Lesson
        fields='__all__'


class ScheduleLessonSerializers(serializers.ModelSerializer):
    teacher = TeacherSerializer()
    lesson=LessonSerializers()
    class Meta:
        model=ScheduleLesson
        fields='__all__'


class ScheduleSerializers(serializers.ModelSerializer):
    schedule_lesson=ScheduleLessonSerializers()
    class Meta:
        model=Schedule
        fields=('schedule_lesson','class_room','counter')










