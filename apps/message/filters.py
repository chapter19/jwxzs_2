#-*- coding:utf-8 -*-
import django_filters
from .models import ReceiverMessage,MessageFile,Message,ReceiverGroup


class OutboxMessageFilter(django_filters.rest_framework.FilterSet):
    send_time=django_filters.DateRangeFilter()
    class Meta:
        model=Message
        fields=['type','send_time','send_state','if_delete','if_collect','if_report_over']


class InboxMessageFilter(django_filters.rest_framework.FilterSet):
    send_time = django_filters.DateRangeFilter(field_name='send_time',help_text='发送时间')
    if_delete=django_filters.BooleanFilter(field_name='receiver_message__if_delete',lookup_expr='exact',help_text='是否回收')
    if_collect=django_filters.BooleanFilter(field_name='receiver_message__if_collect',lookup_expr='exact',help_text='是否收藏')
    if_report=django_filters.BooleanFilter(field_name='receiver_message__if_report',lookup_expr='exact',help_text='是否举报')
    sender_name=django_filters.CharFilter(field_name='sender__name',lookup_expr='icontains',help_text='发送者姓名')
    sender_username=django_filters.CharFilter(field_name='sender__username',lookup_expr='icontains',help_text='发送者用户名')
    class Meta:
        model=Message
        fields=['type','if_delete','if_collect','if_report','sender_name','sender_username','send_time','if_report_over']


class InboxGroupMessageFilter(django_filters.rest_framework.FilterSet):
    send_time = django_filters.DateRangeFilter(field_name='send_time',help_text='发送时间')
    if_delete = django_filters.BooleanFilter(field_name='receiver_group__group_receiver_message__if_delete', lookup_expr='exact',help_text='是否删除')
    if_collect = django_filters.BooleanFilter(field_name='receiver_group__group_receiver_message__if_collect', lookup_expr='exact',help_text='是否收藏')
    if_report = django_filters.BooleanFilter(field_name='receiver_group__group_receiver_message__if_report', lookup_expr='exact',help_text='是否举报')
    group_name=django_filters.CharFilter(field_name='receiver_group__group_name',lookup_expr='icontains',help_text='组织名')
    sender_name = django_filters.CharFilter(field_name='sender__name', lookup_expr='icontains',help_text='发送人姓名')
    sender_username = django_filters.CharFilter(field_name='sender__username', lookup_expr='icontains',help_text='发送人用户名')
    class Meta:
        model = Message
        fields = ['type', 'if_delete', 'if_collect', 'if_report','group_name','sender_name','sender_username','send_time','if_report_over']

# class

