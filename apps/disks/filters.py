#-*- coding:utf-8 -*-
import django_filters

from .models import Folder,FileExtension,File,Label,FolderPath,OpenFolderPath,CheckedUser

class FolderFilter(django_filters.rest_framework.FilterSet):
    delete_time=django_filters.DateTimeFromToRangeFilter(field_name='delete_time',label='删除时间范围',help_text='删除时间范围')
    create_time=django_filters.DateTimeFromToRangeFilter(field_name='create_time',label='创建时间范围',help_text='创建时间范围')
    update_time=django_filters.DateTimeFromToRangeFilter(field_name='update_time',label='修改时间范围',help_text='修改时间范围')
    resume_time = django_filters.DateTimeFromToRangeFilter(field_name='resume_time', label='恢复时间范围', help_text='恢复时间范围')
    if_root = django_filters.BooleanFilter(field_name='parent_folder', lookup_expr='isnull', label='是否为根目录文件',help_text='是否为根目录文件')
    class Meta:
        model=Folder
        fields=['if_open','if_auto_open','if_delete','if_auto_delete','if_auto_resume','delete_time','resume_time','create_time','update_time','disk__id','disk__ower_id','parent_folder_id','if_clone','if_auto_clone','if_root']

class FileExtensionFilter(django_filters.rest_framework.FilterSet):
    class Meta:
        model=FileExtension
        fields=['type']


class FileFilter(django_filters.rest_framework.FilterSet):
    delete_time = django_filters.DateTimeFromToRangeFilter(field_name='delete_time', label='删除时间范围', help_text='删除时间范围')
    create_time = django_filters.DateTimeFromToRangeFilter(field_name='create_time', label='创建时间范围', help_text='创建时间范围')
    update_time = django_filters.DateTimeFromToRangeFilter(field_name='update_time', label='修改时间范围', help_text='修改时间范围')
    resume_time = django_filters.DateTimeFromToRangeFilter(field_name='resume_time', label='恢复时间范围', help_text='恢复时间范围')
    if_root=django_filters.BooleanFilter(field_name='folder',lookup_expr='isnull',label='是否为根目录文件',help_text='是否为根目录文件')
    class Meta:
        model=File
        fields=['if_open','if_auto_open','if_clone','if_auto_clone','if_delete','if_auto_delete','if_auto_resume','resume_time','delete_time','update_time','create_time','folder','if_root']


class LabelFilter(django_filters.rest_framework.FilterSet):
    name=django_filters.CharFilter(field_name='name',lookup_expr='icontains',label='标签名',help_text='标签名',)
    class Meta:
        model=Label
        fields=['name']


class FolderPathFilter(django_filters.rest_framework.FilterSet):
    class Meta:
        model=FolderPath
        fields=['folder_id']

class OpenFolderPathFilter(django_filters.rest_framework.FilterSet):
    class Meta:
        model=OpenFolderPath
        fields=['folder_id']

class CheckedUserFilter(django_filters.rest_framework.FilterSet):
    class Meta:
        model=CheckedUser
        fields=['share_link']