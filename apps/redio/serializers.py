#-*- coding:utf-8 -*-

from rest_framework import serializers

from .models import Redio

class RedioListSerializer(serializers.ModelSerializer):
    time=serializers.DateTimeField(format='%Y-%m-%d %H:%M',help_text='操作时间')
    class Meta:
        model=Redio
        fields=['title','time','id']



class RedioRetrieveSerializer(serializers.ModelSerializer):
    time=serializers.DateTimeField(format='%Y-%m-%d %H:%M',help_text='操作时间')
    class Meta:
        model=Redio
        fields=['title','time','id','body']