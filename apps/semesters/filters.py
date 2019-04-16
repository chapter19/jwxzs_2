#-*- coding:utf-8 -*-
from django_filters.rest_framework import FilterSet
from .models import Semester,CurrentSemester


class SemesterFilter(FilterSet):
    class Meta:
        model=Semester
        fields=['post_code','verbose_name']
