#-*- coding:utf-8 -*-
from rest_framework import serializers

from .models import Log



class LogSerializer(serializers.ModelSerializer):
    action_time=serializers.DateTimeField(format='%Y-%m-%d %H:%M',help_text='操作时间')
    action_type = serializers.SerializerMethodField()
    def get_action_type(self, obj):
        return obj.get_action_type_display()
    class Meta:
        model=Log
        fields=['message','action_type','action_time','ip','address']
