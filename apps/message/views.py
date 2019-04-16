from django.shortcuts import render
# from django.contrib import V
from .models import Message,ReceiverMessage,MessageFile,ReceiverGroup,GroupReceiverMessage
from rest_framework import mixins,viewsets


from .serializers import OutboxMessageSerializer,OutboxMessageCreateSerializer,OutboxMessageUpdateSerializer,\
    OutboxMessageFileCreateSerializer,OutboxMessageReceiverCreateSerializer,InboxMessageReceiverUpdateSerializer,\
    OutboxMessageFileUpdateSerializer,OutboxGroupCreateSerializer,InboxGroupReceiverUpdateSerializer


from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework.pagination import PageNumberPagination
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Q

from users.models import Class,Colloge,Major
from lessons.models import ScheduleLesson

# from .filters import OutboxReceiverFilter,OutboxMessageFileFilter,OutboxMessageFilter,OutboxReceiveGroupFilter,OutboxReceiverGroupReceiverFilter
from .filters import OutboxMessageFilter,InboxGroupMessageFilter,InboxMessageFilter

from utils.permissions import MessageIsOwnerOrReadOnly,OutboxMessageFileIsOwnerOrReadOnly

from users.views import DefaultPagination


#发件箱
class OutboxView(mixins.ListModelMixin,mixins.RetrieveModelMixin,mixins.CreateModelMixin,mixins.UpdateModelMixin,viewsets.GenericViewSet):
    '''
    list:
        发件人获取用户发送的信息
    read:
        发件人获取用户发送信息的详情
    create:
        发件人创建消息
    update:
        发件人更新消息
    '''
    pagination_class = DefaultPagination
    permission_classes = (IsAuthenticated,MessageIsOwnerOrReadOnly,)
    # serializer_class = OutboxMessageSerializer
    ordering_fields=['send_time','id','if_collect','type']
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter,)
    filter_class=OutboxMessageFilter
    def get_serializer_class(self):
        if self.action=='list':
            return OutboxMessageSerializer
        elif self.action=='create':
            return OutboxMessageCreateSerializer
        elif self.action=='update':
            return OutboxMessageUpdateSerializer
        else:
            return OutboxMessageSerializer
    def get_queryset(self):
        return Message.objects.filter(sender=self.request.user)


#发件箱新建文件，做了权限
class OutboxMessageFileView(mixins.CreateModelMixin,mixins.UpdateModelMixin,viewsets.GenericViewSet):
    '''
    create:
        发件人为消息创建文件
    '''
    def get_serializer_class(self):
        if self.action=='create':
            return OutboxMessageFileCreateSerializer
        else:
            return OutboxMessageFileUpdateSerializer
    permission_classes = (IsAuthenticated, OutboxMessageFileIsOwnerOrReadOnly,)
    def get_queryset(self):
        return MessageFile.objects.filter(message__sender=self.request.user)


#创建、修改收件人，做了权限
class MessageReceiverView(mixins.CreateModelMixin,mixins.UpdateModelMixin,viewsets.GenericViewSet):
    '''
    create:
        发件人为消息创建收件人
    update:
        收件人标记收件为已读、收藏、删除
    '''
    permission_classes = (IsAuthenticated,)
    def get_serializer_class(self):
        if self.action=='update':
            return InboxMessageReceiverUpdateSerializer
        else:
            return OutboxMessageReceiverCreateSerializer
    def get_queryset(self):
        if self.action=='create':
            return ReceiverMessage.objects.filter(message__sender=self.request.user)
        else:
            return ReceiverMessage.objects.filter(receiver=self.request.user)


#发件人创建接收组 没做完权限 做了课程班级的
class OutboxMessageGroupCreateView(mixins.CreateModelMixin,viewsets.GenericViewSet):
    '''
    create:
        发件人创建接收组
    '''
    permission_classes = (IsAuthenticated,)
    serializer_class = OutboxGroupCreateSerializer
    def get_queryset(self):
        return ReceiverGroup.objects.filter(message__sender=self.request.user)



#群组收件箱修改
class MessageGroupReceiverView(mixins.UpdateModelMixin,viewsets.GenericViewSet):
    '''
    update:
        收件人标记群组收件为已读、收藏、删除、举报
    '''
    permission_classes = (IsAuthenticated,)
    serializer_class=InboxGroupReceiverUpdateSerializer
    def get_queryset(self):
        return GroupReceiverMessage.objects.filter(receiver=self.request.user)



#收件箱
class InboxReceiverMessageView(mixins.ListModelMixin,viewsets.GenericViewSet):
    '''
    list:
        收件人收件列表
    '''
    pagination_class = DefaultPagination
    permission_classes = (IsAuthenticated,)
    # serializer_class = OutboxMessageSerializer
    ordering_fields = ['send_time', 'id', 'receiver_message__if_collect','receiver_message__read_time','type']
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter,)
    filter_class=InboxMessageFilter
    def get_serializer_class(self):
        return OutboxMessageSerializer
    def get_queryset(self):
        return Message.objects.filter(receiver_message__receiver=self.request.user)


#收件箱群组邮件
class InboxGroupReceiverView(mixins.ListModelMixin,viewsets.GenericViewSet):
    '''
    list:
        收件人收群组邮件列表
    '''
    pagination_class = DefaultPagination
    permission_classes = (IsAuthenticated,)
    # serializer_class = OutboxMessageSerializer
    ordering_fields = ['send_time', 'id','receiver_group__group_receiver_message__read_time','receiver_group__group_receiver_message__if_collect','type']
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter,)
    filter_class=InboxGroupMessageFilter
    def get_serializer_class(self):
        return OutboxMessageSerializer
    def get_queryset(self):
        return Message.objects.filter(receiver_group__group_receiver_message__receiver=self.request.user)


