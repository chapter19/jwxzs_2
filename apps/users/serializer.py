#-*- coding:utf-8 -*-
from .models import Major,Colloge,Class,Teacher,Student,StudentDetail
from rest_framework import serializers


class MajorSerializer(serializers.ModelSerializer):
    class Meta:
        model=Major
        fields='__all__'


class ClassMajorSerializer(serializers.ModelSerializer):
    class Meta:
        model=Major
        fields=['name','subject','degree']


class CollogeSerializer(serializers.ModelSerializer):
    class Meta:
        model=Colloge
        fields=['name']


class ClassSerializer(serializers.ModelSerializer):
    colloge=CollogeSerializer()
    major=ClassMajorSerializer()
    class Meta:
        model=Class
        fields=['name','colloge','major','grade']


class TeacherSerializer(serializers.ModelSerializer):
    gender=serializers.SerializerMethodField()
    def get_gender(self, obj):
        return obj.get_gender_display()
    class Meta:
        model=Teacher
        fields = '__all__'


class StudentSerializer(serializers.ModelSerializer):
    gender=serializers.SerializerMethodField()
    cla=ClassSerializer()
    def get_gender(self, obj):
        return obj.get_gender_display()
    class Meta:
        model=Student
        fields='__all__'


class StudentDetailSerializer(serializers.ModelSerializer):
    base_data=StudentSerializer()
    class Meta:
        model=StudentDetail
        fields='__all__'