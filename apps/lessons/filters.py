#-*- coding:utf-8 -*-

from rest_framework import generics
import django_filters
from .models import Schedule
from users.models import Student

class StudentScheduleFilter(django_filters.rest_framework.FilterSet):
    '''
    学生课表过滤
    '''
    class Meta:
        model=Schedule
        fields=['schedule_lesson__semester','schedule_lesson__score__student__id']


class TeacherScheduleFilter(django_filters.rest_framework.FilterSet):
    '''
    教师课表过滤
    '''
    class Meta:
        model=Schedule
        fields=['schedule_lesson__semester','schedule_lesson__teacher__id']









