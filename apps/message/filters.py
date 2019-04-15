# #-*- coding:utf-8 -*-
#
# import django_filters
# from .models import ReceiverMessage,MessageFile,Message,ReceiverGroup
#
# class OutboxReceiverFilter(django_filters.rest_framework.FilterSet):
#     message_id=django_filters.NumberFilter(field_name='message__id',lookup_expr='exact',help_text='消息id')
#     class Meta:
#         model=ReceiverMessage
#         fields=['message_id',]
#
#
# class OutboxReceiverGroupReceiverFilter(django_filters.rest_framework.FilterSet):
#     group__id=django_filters.NumberFilter(field_name='group__id',lookup_expr='exact',help_text='所在消息组id')
#     class Meta:
#         model=ReceiverMessage
#         fields=['group_id']
#
#
#
# class OutboxMessageFileFilter(django_filters.rest_framework.FilterSet):
#     message_id=django_filters.NumberFilter(field_name='message__id',lookup_expr='exact',help_text='消息id')
#     class Meta:
#         model=MessageFile
#         fields=['message_id']
#
#
# class OutboxMessageFilter(django_filters.rest_framework.FilterSet):
#     title=django_filters.CharFilter(field_name='title',lookup_expr='icontains',help_text='标题')
#     body=django_filters.CharFilter(field_name='body',lookup_expr='icontains',help_text='内容')
#     # type=django_filters.ChoiceFilter(field_name='')
#     class Meta:
#         model=Message
#         fields=['title','type','body','send_state','reply_message__title','reply_message__body','if_delete','if_collect']
#
#
# class OutboxReceiveGroupFilter(django_filters.rest_framework.FilterSet):
#     message_id=django_filters.CharFilter(field_name='message__id',lookup_expr='exact',help_text='消息id')
#     class Meta:
#         model=ReceiverGroup
#         fields=['message_id']
#
#
#
# # class OutboxReceiverClassFilter(django_filters.rest_framework.FilterSet):
# #     message_id = django_filters.NumberFilter(field_name='message__id', lookup_expr='exact', help_text='消息id')
# #     class Meta:
# #         model=ReceiverClass
# #         fields=['message_id']
#
