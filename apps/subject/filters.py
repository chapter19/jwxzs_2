#-*- coding:utf-8 -*-
import django_filters
from .models import StepOneLessonTeacher

class StepOneLessonTeacherFilter(django_filters.rest_framework.FilterSet):
    class Meta:
        model=StepOneLessonTeacher
        fields=['lesson_id']

