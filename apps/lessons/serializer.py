#-*- coding:utf-8 -*-
from rest_framework import serializers
from .models import Schedule,ScheduleLesson,Lesson,MajorLesson
from users.serializer import TeacherSerializer
from semesters.models import Semester
from django.forms.models import model_to_dict


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


class StudentScheduleSemesterCountSerializer(serializers.Serializer):
    student_id=serializers.CharField(max_length=12,min_length=10,help_text='学号',label='学号',write_only=True,required=True)
    def create(self, validated_data):
        student_id=validated_data.get('student_id')
        list=ScheduleLesson.objects.filter(score__student_id=student_id,teacher__isnull=False).values('semester').distinct().order_by('-semester')
        retu_list=[]
        for li in list:
            semester=Semester.objects.filter(post_code=li['semester']).values('post_code','verbose_name')[0]
            retu_list.append(semester)
        return retu_list


class TeacherScheduleSemesterCountSerializer(serializers.Serializer):
    teacher_id=serializers.CharField(max_length=6,min_length=5,help_text='教号',label='教号',write_only=True,required=True)
    def create(self, validated_data):
        teacher_id=validated_data.get('teacher_id')
        list=ScheduleLesson.objects.filter(teacher_id=teacher_id).values('semester').distinct().order_by('semester')
        retu_list = []
        for li in list:
            semester = Semester.objects.filter(post_code=li['semester']).values('post_code', 'verbose_name')[0]
            retu_list.append(semester)
        return retu_list


class MajorLessonSerializer(serializers.ModelSerializer):
    lesson=LessonSerializers()
    lesson_type=serializers.SerializerMethodField()
    def get_lesson_type(self,obj):
        return obj.get_lesson_type_display()
    class Meta:
        model=MajorLesson
        fields='__all__'


class TeacherScheduleLessonSerializer(serializers.ModelSerializer):
    teacher=TeacherSerializer()
    lesson=LessonSerializers()
    class Meta:
        model=ScheduleLesson
        fields='__all__'


