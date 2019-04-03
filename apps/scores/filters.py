#-*- coding:utf-8 -*-

import django_filters
from .models import Score,TotalCredit

class ScoreFilter(django_filters.rest_framework.FilterSet):
    semester = django_filters.CharFilter(field_name='schedule_lesson__semester', help_text='学期')
    class Meta:
        model=Score
        fields=['semester',
                # 'student__id',
                ]


class ScoreStudentListFilter(django_filters.rest_framework.FilterSet):
    id = django_filters.CharFilter(field_name='schedule_lesson__id', help_text='课程表课程id')
    class Meta:
        model=Score
        fields=['id']


class TotalCreditFilter(django_filters.rest_framework.FilterSet):
    student_id=django_filters.CharFilter(field_name='student__id',help_text='学号')
    class Meta:
        model=TotalCredit
        fields=['student_id']





