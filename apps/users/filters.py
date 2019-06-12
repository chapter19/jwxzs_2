#-*- coding:utf-8 -*-
import django_filters

from .models import Student,Teacher,Class,Colloge,Major,Department,UserProfile

class StudentFilters(django_filters.rest_framework.FilterSet):
    grade_min=django_filters.NumberFilter(field_name='cla__grade',lookup_expr='gte',help_text='年级大于等于')
    grade_max=django_filters.NumberFilter(field_name='cla__grade',lookup_expr='lte',help_text='年级小于等于')
    class_id = django_filters.CharFilter(field_name='cla__id', help_text='班级号',)
    class_name=django_filters.CharFilter(field_name='cla__name',help_text='班级名',lookup_expr='contains')
    grade=django_filters.NumberFilter(field_name='cla__grade',lookup_expr='exact',help_text='年级')
    major_id=django_filters.CharFilter(field_name='cla__major__major_id',help_text='专业号')
    major_name=django_filters.CharFilter(field_name='cla__major__name',help_text='专业名')
    colloge_id=django_filters.CharFilter(field_name='cla__colloge__id',help_text='学院号')
    colloge_name=django_filters.CharFilter(field_name='cla__colloge__name',help_text='学院名',lookup_expr='contains')
    name=django_filters.CharFilter(field_name='name',help_text='学生姓名',label='学生姓名',lookup_expr='icontains')
    class Meta:
        model = Student
        fields = ['id','name','gender','class_id','class_name','grade','major_id','colloge_id','colloge_name','grade_min','grade_max']


class TeacherFilters(django_filters.rest_framework.FilterSet):
    department_name=django_filters.CharFilter(field_name='department__name',lookup_expr='icontains',help_text='单位')
    name=django_filters.CharFilter(field_name='name',lookup_expr='icontains',help_text='姓名')
    id=django_filters.CharFilter(field_name='id',lookup_expr='icontains',help_text='教号')
    class Meta:
        model=Teacher
        fields=['department_name','id','name','gender','department_id']


class ClassFilters(django_filters.rest_framework.FilterSet):
    colloge_id=django_filters.CharFilter(field_name='colloge_id',lookup_expr='exact',help_text='学院id')
    major_id=django_filters.NumberFilter(field_name='major_id',lookup_expr='exact',help_text='专业id')
    name=django_filters.CharFilter(field_name='name',lookup_expr='icontains',help_text='班级名')
    class Meta:
        model=Class
        fields=['grade','colloge_id','major_id','name','id']


class CollogeFilters(django_filters.rest_framework.FilterSet):
    id=django_filters.CharFilter(field_name='id',lookup_expr='exact',help_text='学院id')
    name=django_filters.CharFilter(field_name='name',lookup_expr='icontains',help_text='学院名')
    class Meta:
        model=Colloge
        fields=['id','name',]


class MajorFilter(django_filters.rest_framework.FilterSet):
    name=django_filters.CharFilter(field_name='name',lookup_expr='icontains',help_text='专业名')
    class Meta:
        model=Major
        fields=['id','major_id','name','grade']

class DepartmentFilter(django_filters.rest_framework.FilterSet):
    name = django_filters.CharFilter(field_name='name', lookup_expr='icontains', help_text='专业名')
    class Meta:
        model = Department
        fields = ['id','name']

class UserFilter(django_filters.rest_framework.FilterSet):
    # student_class_name=django_filters.CharFilter(field_name='student__class__name',lookup_expr='icontains',help_text='学生班级名',label='学生班级名')
    # student_class_colloge_name=django_filters.CharFilter(field_name='student__class__colloge__name',lookup_expr='icontains',help_text='学生学院名',label='学生班级名')
    name = django_filters.CharFilter(field_name='name', help_text='姓名', label='姓名', lookup_expr='icontains')
    username = django_filters.CharFilter(field_name='username', help_text='用户名', label='用户名', lookup_expr='icontains')
    class Meta:
        model=UserProfile
        fields=['username','gender','name','is_student','is_teacher','student__cla__grade','student__cla__id','teacher__department__id']