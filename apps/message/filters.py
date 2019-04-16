#-*- coding:utf-8 -*-
import django_filters
from .models import ReceiverMessage,MessageFile,Message,ReceiverGroup


class OutboxMessageFilter(django_filters.rest_framework.FilterSet):
    send_time=django_filters.DateRangeFilter()
    class Meta:
        model=Message
        fields=['type','send_time','send_state','if_delete','if_collect','if_report_over']


class InboxMessageFilter(django_filters.rest_framework.FilterSet):
    send_time = django_filters.DateRangeFilter(field_name='send_time')
    if_delete=django_filters.BooleanFilter(field_name='receiver_message__if_delete',lookup_expr='exact')
    if_collect=django_filters.BooleanFilter(field_name='receiver_message__if_collect',lookup_expr='exact')
    if_report=django_filters.BooleanFilter(field_name='receiver_message__if_report',lookup_expr='exact')
    sender_name=django_filters.CharFilter(field_name='sender__name',lookup_expr='icontains')
    sender_username=django_filters.CharFilter(field_name='sender__username',lookup_expr='icontains')
    class Meta:
        model=Message
        fields=['type','if_delete','if_collect','if_report','sender_name','sender_username','send_time','if_report_over']


class InboxGroupMessageFilter(django_filters.rest_framework.FilterSet):
    send_time = django_filters.DateRangeFilter(field_name='send_time')
    if_delete = django_filters.BooleanFilter(field_name='receiver_group__group_receiver_message__if_delete', lookup_expr='exact')
    if_collect = django_filters.BooleanFilter(field_name='receiver_group__group_receiver_message__if_collect', lookup_expr='exact')
    if_report = django_filters.BooleanFilter(field_name='receiver_group__group_receiver_message__if_report', lookup_expr='exact')
    group_name=django_filters.CharFilter(field_name='receiver_group__group_name',lookup_expr='icontains')
    sender_name = django_filters.CharFilter(field_name='sender__name', lookup_expr='icontains')
    sender_username = django_filters.CharFilter(field_name='sender__username', lookup_expr='icontains')
    class Meta:
        model = Message
        fields = ['type', 'if_delete', 'if_collect', 'if_report','group_name','sender_name','sender_username','send_time','if_report_over']

# class

