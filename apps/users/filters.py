#-*- coding:utf-8 -*-
import django_filters
from .models import Student

class StudentFilters(django_filters.rest_framework.FilterSet):
    grade_min=django_filters.NumberFilter(field_name='cla__grade',lookup_expr='gte',help_text='年级大于等于')
    grade_max=django_filters.NumberFilter(field_name='cla__grade',lookup_expr='lte',help_text='年级小于等于')
    class_id = django_filters.CharFilter(field_name='cla__id', help_text='班级号',)
    class_name=django_filters.CharFilter(field_name='cla__name',help_text='班级名',lookup_expr='contains')
    grade=django_filters.CharFilter(field_name='cla__grade',help_text='年级')
    major_id=django_filters.CharFilter(field_name='cla__major__major_id',help_text='专业号')
    major_name=django_filters.CharFilter(field_name='cla__major__name',help_text='专业名')
    colloge_id=django_filters.CharFilter(field_name='cla__colloge__id',help_text='学院号')
    colloge_name=django_filters.CharFilter(field_name='cla__colloge__name',help_text='学院名',lookup_expr='contains')
    class Meta:
        model = Student
        fields = ['id','name','gender','class_id','class_name','grade','major_id','colloge_id','colloge_name','grade_min','grade_max']


