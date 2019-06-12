from django.shortcuts import render
from rest_framework import mixins,viewsets
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters,status
from rest_framework.response import Response
from datetime import datetime

from .models import Message,ReceiverMessage,MessageFile,ReceiverGroup,GroupReceiverMessage
from .serializers import OutboxMessageSerializer,OutboxMessageCreateSerializer,OutboxMessageUpdateSerializer,\
    OutboxMessageFileCreateSerializer,OutboxMessageReceiverCreateSerializer,InboxMessageReceiverUpdateSerializer,\
    OutboxGroupCreateSerializer,InboxGroupReceiverUpdateSerializer,\
    ReceiverUpdateByQuerySerailizer,GroupReceiverUpdateByQuerySerailizer,SenderUpdateByQuerySerializer,\
    OneKeyToReadSerializer
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
    ordering_fields=['send_time','id','if_collect','type','title']
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter,)
    filter_class=OutboxMessageFilter
    def get_serializer_class(self):
        if self.action=='list' or self.action=='retrieve':
            return OutboxMessageSerializer
        elif self.action=='create':
            return OutboxMessageCreateSerializer
        else:
            return OutboxMessageUpdateSerializer
    def get_queryset(self):
        return Message.objects.filter(sender=self.request.user)


#发件箱新建文件，做了权限
class OutboxMessageFileView(mixins.CreateModelMixin,mixins.DestroyModelMixin,viewsets.GenericViewSet):
    '''
    create:
        发件人为消息创建文件
    delete:
        删除消息文件
    '''
    def get_serializer_class(self):
        if self.action=='create':
            return OutboxMessageFileCreateSerializer
        # else:
        #     return OutboxMessageFileUpdateSerializer
    permission_classes = (IsAuthenticated, OutboxMessageFileIsOwnerOrReadOnly,)
    def get_queryset(self):
        return MessageFile.objects.filter(message__sender=self.request.user)
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        message=instance.message
        user=self.request.user
        if user!=message.sender:
            return Response(status=status.HTTP_403_FORBIDDEN)
        if message.send_state==1:
            return Response(status=status.HTTP_403_FORBIDDEN)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
    def perform_destroy(self, instance):
        instance.delete()


#创建、修改收件人，做了权限
class MessageReceiverView(mixins.CreateModelMixin,mixins.DestroyModelMixin,viewsets.GenericViewSet):
    '''
    create:
        发件人为消息创建收件人
    delete:
        删除收件人
    '''
    permission_classes = (IsAuthenticated,)
    def get_serializer_class(self):
        # if self.action=='update':
        #     return InboxMessageReceiverUpdateSerializer
        # else:
        return OutboxMessageReceiverCreateSerializer
    def get_queryset(self):
        # if self.action=='create':
        return ReceiverMessage.objects.filter(message__sender=self.request.user)
        # else:
        #     return ReceiverMessage.objects.filter(receiver=self.request.user)
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        message=instance.message
        user=self.request.user
        if user!=message.sender:
            return Response(status=status.HTTP_403_FORBIDDEN)
        if message.send_state==1:
            return Response(status=status.HTTP_403_FORBIDDEN)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
    def perform_destroy(self, instance):
        instance.delete()


#发件人创建接收组 没做完权限 做了课程班级的
class OutboxMessageGroupView(mixins.CreateModelMixin,mixins.DestroyModelMixin,viewsets.GenericViewSet):
    '''
    create:
        发件人创建接收组
    delete:
        删除接受组
    '''
    permission_classes = (IsAuthenticated,)
    serializer_class = OutboxGroupCreateSerializer
    def get_queryset(self):
        return ReceiverGroup.objects.filter(message__sender=self.request.user)
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        user=self.request.user
        message=instance.receiver_group.message
        if user!=message.sender:
            return Response(status=status.HTTP_403_FORBIDDEN)
        if message.send_state==1:
            return Response(status=status.HTTP_403_FORBIDDEN)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
    def perform_destroy(self, instance):
        instance.delete()


#群组收件箱修改
# class MessageGroupReceiverView(mixins.UpdateModelMixin,viewsets.GenericViewSet):
#     '''
#     update:
#         收件人标记群组收件为已读、收藏、删除、举报
#     '''
#     permission_classes = (IsAuthenticated,)
#     serializer_class=InboxGroupReceiverUpdateSerializer
#     def get_queryset(self):
#         return GroupReceiverMessage.objects.filter(receiver=self.request.user)
#


#收件箱
class InboxReceiverMessageView(mixins.ListModelMixin,mixins.RetrieveModelMixin,viewsets.GenericViewSet):
    '''
    list:
        收件人收件列表
    retrieve:
        收件人收件消息详情
    '''
    pagination_class = DefaultPagination
    permission_classes = (IsAuthenticated,)
    # serializer_class = OutboxMessageSerializer
    ordering_fields = ['send_time', 'id', 'receiver_message__if_collect','receiver_message__read_time','type','title']
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter,)
    filter_class=InboxMessageFilter
    def get_serializer_class(self):
        return OutboxMessageSerializer
    def get_queryset(self):
        return Message.objects.filter(receiver_message__receiver=self.request.user,send_state=1)
    def retrieve(self, request, *args, **kwargs):
        user=self.request.user
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        receiver_message=ReceiverMessage.objects.filter(receiver=user,message_id=instance.id)
        if receiver_message:
            receiver_message=receiver_message[0]
            if receiver_message.read_time==None:
                receiver_message.read_time=datetime.now()
                receiver_message.save()
        return Response(serializer.data)


#收件箱群组邮件
class InboxGroupReceiverView(mixins.ListModelMixin,mixins.RetrieveModelMixin,viewsets.GenericViewSet):
    '''
    list:
        收件人收群组邮件列表
    retrieve:
        收件人收群组消息详情
    '''
    pagination_class = DefaultPagination
    permission_classes = (IsAuthenticated,)
    # serializer_class = OutboxMessageSerializer
    ordering_fields = ['send_time', 'id','receiver_group__group_receiver_message__read_time','receiver_group__group_receiver_message__if_collect','type','title']
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter,)
    filter_class=InboxGroupMessageFilter
    def get_serializer_class(self):
        return OutboxMessageSerializer
    def get_queryset(self):
        return Message.objects.filter(receiver_group__group_receiver_message__receiver=self.request.user,send_state=1)
    def retrieve(self, request, *args, **kwargs):
        user=self.request.user
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        group_receiver_message=GroupReceiverMessage.objects.filter(receiver=user,receiver_group__message_id=instance.id)
        if group_receiver_message:
            group_receiver_message=group_receiver_message[0]
            if group_receiver_message.read_time==None:
                group_receiver_message.read_time=datetime.now()
                group_receiver_message.save()
        return Response(serializer.data)

#批量更改
class ReceiverUpdateByQueryView(mixins.CreateModelMixin,viewsets.GenericViewSet):
    '''
    create:
        收件人批量更改消息
    '''
    def get_serializer_class(self):
        return ReceiverUpdateByQuerySerailizer
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(status=status.HTTP_201_CREATED, headers=headers)
    def perform_create(self, serializer):
        serializer.save()

class GroupReceiverUpdateByQueryView(mixins.CreateModelMixin,viewsets.GenericViewSet):
    '''
    create:
        收件人批量更改群组消息
    '''
    def get_serializer_class(self):
        return GroupReceiverUpdateByQuerySerailizer
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(status=status.HTTP_201_CREATED, headers=headers)
    def perform_create(self, serializer):
        serializer.save()

class SenderUpdateByQueryView(mixins.CreateModelMixin,viewsets.GenericViewSet):
    '''
    create:
        发件人批量更改消息
    '''
    def get_serializer_class(self):
        return SenderUpdateByQuerySerializer
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(status=status.HTTP_201_CREATED, headers=headers)
    def perform_create(self, serializer):
        serializer.save()


class OneKeyToReadView(mixins.CreateModelMixin,viewsets.GenericViewSet):
    '''
    create:
        一键标记已读
    '''
    def get_serializer_class(self):
        return OneKeyToReadSerializer
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(status=status.HTTP_201_CREATED, headers=headers)
    def perform_create(self, serializer):
        serializer.save()