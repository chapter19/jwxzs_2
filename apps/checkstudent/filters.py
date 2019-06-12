#-*- coding:utf-8 -*-
import django_filters
from .models import TheCheck,CheckedStudent

class TheCheckFilter(django_filters.rest_framework.FilterSet):
    start_time=django_filters.DateTimeFromToRangeFilter(field_name='start_time',help_text='发起时间')
    password=django_filters.NumberFilter(field_name='password',lookup_expr='exact',help_text='密码')
    schedule_lesson=django_filters.NumberFilter(field_name='schedule_lesson_id',lookup_expr='exact',help_text='课程班级')
    if_not_checked = django_filters.BooleanFilter(method='if_check_method', help_text='是否未点到', label='是否未点到')
    def if_check_method(self, queryset, name, value):
        return queryset.filter(checked_student__check_time__isnull=value)
    class Meta:
        model=TheCheck
        fields=['start_time','password','schedule_lesson','if_not_checked']



class CheckedStudentFilter(django_filters.rest_framework.FilterSet):
    the_check=django_filters.NumberFilter(field_name='the_check_id',help_text='点到id')
    schedule_lesson=django_filters.NumberFilter(field_name='the_check__schedule_lesson_id',lookup_expr='exact',help_text='课程班级')
    student=django_filters.NumberFilter(field_name='student_id',lookup_expr='exact',help_text='学生的用户id')
    if_not_checked = django_filters.BooleanFilter(method='if_check_method', help_text='是否未点到', label='是否未点到')
    def if_check_method(self, queryset, name, value):
        return queryset.filter(check_time__isnull=value)
    class Meta:
        model=CheckedStudent
        fields=['the_check','schedule_lesson','student','if_not_checked']

