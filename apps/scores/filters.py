#-*- coding:utf-8 -*-

import django_filters
from .models import Score,TotalCredit

class ScoreFilter(django_filters.rest_framework.FilterSet):
    class Meta:
        model=Score
        fields=['schedule_lesson__semester','student__id']


class ScoreStudentListFilter(django_filters.rest_framework.FilterSet):
    class Meta:
        model=Score
        fields=['schedule_lesson__id']


class TotalCreditFilter(django_filters.rest_framework.FilterSet):
    class Meta:
        model=TotalCredit
        fields=['student__id']





