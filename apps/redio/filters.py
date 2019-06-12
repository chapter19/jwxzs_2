#-*- coding:utf-8 -*-

import django_filters

from .models import Redio


class RedioFilter(django_filters.rest_framework.FilterSet):
    title=django_filters.CharFilter(field_name='title',lookup_expr='icontains',help_text='标题',label='标题')
    time_range=django_filters.DateTimeFromToRangeFilter(field_name='time',lookup_expr='gte',help_text='发布时间区间',label='发布时间区间')
    class Meta:
        model=Redio
        fields=['title','time_range']


