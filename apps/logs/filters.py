#-*- coding:utf-8 -*-

import django_filters
from .models import Log


class LogFilter(django_filters.rest_framework.FilterSet):
    message=django_filters.CharFilter(field_name='message',lookup_expr='icontains',help_text='操作内容',label='操作内容')
    action_time=django_filters.DateTimeFromToRangeFilter(field_name='action_time',help_text='操作时间',label='操作时间')
    address=django_filters.CharFilter(field_name='address',lookup_expr='icontains',help_text='地址',label='地址')
    class Meta:
        model=Log
        fields=['action_time','action_type','address','message']