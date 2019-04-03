#-*- coding:utf-8 -*-
from .models import Teacher,Student
from rest_framework import serializers


class TeacherSerializer(serializers.ModelSerializer):
    gender=serializers.SerializerMethodField()
    def get_gender(self, obj):
        return obj.get_gender_display()
    class Meta:
        model=Teacher
        fields = '__all__'



class StudentSerializer(serializers.ModelSerializer):
    gender=serializers.SerializerMethodField()
    def get_gender(self, obj):
        return obj.get_gender_display()
    class Meta:
        model=Student
        fields='__all__'


