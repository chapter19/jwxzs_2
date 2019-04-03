#-*- coding:utf-8 -*-
from rest_framework import generics
import django_filters
from .models import Schedule
from users.models import Student

class StudentScheduleFilter(django_filters.rest_framework.FilterSet):
    '''
    学生课表过滤
    '''
    semester=django_filters.CharFilter(field_name='schedule_lesson__semester',help_text='学期')
    class Meta:
        model=Schedule
        fields=[
                'semester',
                # 'schedule_lesson__score__student__id',
                ]


class TeacherScheduleFilter(django_filters.rest_framework.FilterSet):
    '''
    教师课表过滤
    '''
    semester=django_filters.CharFilter(field_name='schedule_lesson__semester',help_text='学期')
    class Meta:
        model=Schedule
        fields=[
                'semester',
                # 'schedule_lesson__teacher__id',
                ]









