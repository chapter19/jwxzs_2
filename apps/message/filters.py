#-*- coding:utf-8 -*-
import django_filters
from .models import ReceiverMessage,MessageFile,Message,ReceiverGroup


class OutboxMessageFilter(django_filters.rest_framework.FilterSet):
    send_time=django_filters.DateRangeFilter()
    title=django_filters.CharFilter(field_name='title',lookup_expr='icontains',label='标题',help_text='标题')
    receiver_name=django_filters.CharFilter(field_name='receiver_message__receiver__name',lookup_expr='icontains',label='收件人姓名',help_text='收件人姓名')
    receiver_username=django_filters.CharFilter(field_name='receiver_message__receiver__username',lookup_expr='icontains',label='收件人用户名',help_text='收件人用户名')
    receiver_group_name=django_filters.CharFilter(field_name='receiver_group__group__group_name',lookup_expr='icontains',label='接受组织名',help_text='接受组织名')
    receiver_group_type=django_filters.CharFilter(field_name='receiver_group__group__group_type',lookup_expr='icontains',label='接受组织类型',help_text='接受组织类型')
    class Meta:
        model=Message
        fields=['type','send_time','send_state','if_delete','if_collect','if_report_over','title','receiver_name','receiver_username','receiver_group_name','receiver_group_type','reply_message']


class InboxMessageFilter(django_filters.rest_framework.FilterSet):
    send_time = django_filters.DateRangeFilter(field_name='send_time',help_text='发送时间')
    if_delete=django_filters.BooleanFilter(field_name='receiver_message__if_delete',lookup_expr='exact',help_text='是否回收',label='是否回收')
    if_collect=django_filters.BooleanFilter(field_name='receiver_message__if_collect',lookup_expr='exact',help_text='是否收藏',label='是否收藏')
    if_report=django_filters.BooleanFilter(field_name='receiver_message__if_report',lookup_expr='exact',help_text='是否举报',label='是否举报')
    sender_name=django_filters.CharFilter(field_name='sender__name',lookup_expr='icontains',help_text='发送者姓名',label='发送者姓名')
    sender_username=django_filters.CharFilter(field_name='sender__username',lookup_expr='icontains',help_text='发送者用户名',label='发送者用户名')
    title=django_filters.CharFilter(field_name='title',lookup_expr='icontains',help_text='标题',label='标题')
    class Meta:
        model=Message
        fields=['type','if_delete','if_collect','if_report','sender_name','sender_username','send_time','if_report_over','title','reply_message']


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
        fields = ['type', 'if_delete', 'if_collect', 'if_report','group_name','sender_name','sender_username','send_time','if_report_over','title','reply_message']

# class

