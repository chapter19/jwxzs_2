#-*- coding:utf-8 -*-
from rest_framework import generics
import django_filters
from .models import Schedule,MajorLesson,ScheduleLesson
# from users.models import Student

class StudentScheduleFilter(django_filters.rest_framework.FilterSet):
    '''
    学生课表过滤
    '''
    semester=django_filters.CharFilter(field_name='schedule_lesson__semester',help_text='学期',label='学期')
    student_id=django_filters.CharFilter(field_name='schedule_lesson__score__student__id',help_text='学号',label='学号')
    class Meta:
        model=Schedule
        fields=[
                'semester',
                'student_id',
                ]


class TeacherScheduleFilter(django_filters.rest_framework.FilterSet):
    '''
    教师课表过滤
    '''
    semester=django_filters.CharFilter(field_name='schedule_lesson__semester',help_text='学期',label='学期')
    teacher_id=django_filters.CharFilter(field_name='schedule_lesson__teacher__id',help_text='教号',label='教号')
    class Meta:
        model=Schedule
        fields=[
                'semester',
                'teacher_id',
                ]


class MajorLessonFilter(django_filters.rest_framework.FilterSet):
    student_id=django_filters.CharFilter(field_name='major__cla__stu__id',lookup_expr='exact',help_text='学号',label='学号')
    # open_semester=django_filters.NumberFilter(field_name='open_semester',lookup_expr='exact',help_text='开课学期',label='开课学期')
    class Meta:
        model=MajorLesson
        fields=['student_id','open_semester','lesson_type']


class TeacherScheduleLessonFilter(django_filters.rest_framework.FilterSet):
    lesson__name=django_filters.CharFilter(field_name='lesson__name',lookup_expr='icontains',help_text='课程名',label='课程名')
    class_name=django_filters.CharFilter(field_name='class_name',lookup_expr='icontains',help_text='课程班级名',label='课程班级名')
    class Meta:
        model=ScheduleLesson
        fields=['semester','lesson__name','class_name','teacher']


class StudentScheduleLessonFilter(django_filters.rest_framework.FilterSet):
    lesson__name = django_filters.CharFilter(field_name='lesson__name', lookup_expr='icontains', help_text='课程名',
                                             label='课程名')
    class_name = django_filters.CharFilter(field_name='class_name', lookup_expr='icontains', help_text='课程班级名',
                                           label='课程班级名')
    class Meta:
        model=ScheduleLesson
        fields=['semester','lesson__name','class_name','teacher','score__student']

