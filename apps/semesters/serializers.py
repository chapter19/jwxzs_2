#-*- coding:utf-8 -*-

from rest_framework import serializers
from .models import Semester,CurrentSemester

class SemesterSerializer(serializers.ModelSerializer):
    class Meta:
        model=Semester
        fields=['post_code','verbose_name']


class CurrentSemesterSerializer(serializers.ModelSerializer):
    current_semester=SemesterSerializer()
    class Meta:
        model=CurrentSemester
        fields=['current_semester']