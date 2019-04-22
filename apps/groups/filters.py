#-*- coding:utf-8 -*-
import django_filters

from .models import Group

class GroupFilter(django_filters.rest_framework.FilterSet):
    group_type=django_filters.NumberFilter(field_name='group_type',lookup_expr='exact',help_text='组织类型')
    group_id=django_filters.NumberFilter(field_name='group_id',lookup_expr='exact',help_text='组织id')
    group_name=django_filters.NumberFilter(field_name='group_name',lookup_expr='icontains',help_text='组织名')
    class Meta:
        model=Group
        fields=['group_type','group_id','group_name']


