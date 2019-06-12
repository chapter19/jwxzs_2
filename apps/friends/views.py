from django.shortcuts import render
from rest_framework import mixins
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from django.db.models import Q

from .filters import CollectFriendsFilter,RecentContactFilter
from .models import CollectFriends
from .serializers import CollectFriendsSerializer,CreateCollectFriendsSerializer,RecentContactSerializer
from .models import RecentContact
from users.views import DefaultPagination
from .tasks import collect_friend_log,send_collect_message
from users.models import UserProfile
from users.serializer import UserSerializer


class CollectFriendsView(mixins.ListModelMixin,mixins.CreateModelMixin,mixins.DestroyModelMixin,viewsets.GenericViewSet):
    '''
    list:
        收藏好友列表
    create:
        关注好友
    delete:
        取消关注好友
    '''
    def get_queryset(self):
        return CollectFriends.objects.all()
    def get_serializer_class(self):
        if self.action=='create':
            return CreateCollectFriendsSerializer
        else:
            return CollectFriendsSerializer
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        try:
            collect_friend_log.delay(request.META.get('REMOTE_ADDR'),request.user.id,request._request.POST.get('friend_id',''))
        except:
            print('获取创建关注好友日志参数失败')
        try:
            send_collect_message.delay(request.user.id,request._request.POST.get('friend_id',''))
        except:
            print('发送关注好友消息异常')
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    pagination_class = DefaultPagination
    permission_classes = (IsAuthenticated,)
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter,)
    filter_class = CollectFriendsFilter
    ordering_fields = ('friend__name', 'friend__username', 'add_time')



class RecentContactView(mixins.ListModelMixin,viewsets.GenericViewSet):
    '''
    list:
        最近联系人列表
    '''
    def get_queryset(self):
        return RecentContact.objects.filter(user=self.request.user)
    def get_serializer_class(self):
        if self.action=='list':
            return RecentContactSerializer
    pagination_class = DefaultPagination
    permission_classes = (IsAuthenticated,)
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter,)
    filter_class = RecentContactFilter
    ordering_fields = ('contact__name', 'contact__username', 'add_time')


class SomeStudentMaybeKnowView(mixins.ListModelMixin,viewsets.GenericViewSet):
    pagination_class = DefaultPagination
    permission_classes = (IsAuthenticated,)
    serializer_class = UserSerializer
    def get_queryset(self):
        user=self.request.user
        if user.is_student:
            return UserProfile.objects.filter(student__score__schedule_lesson__score__student__user=user).exclude(who_collect_me__user=user).order_by('?')[:20]
        elif user.is_teacher:
            return UserProfile.objects.filter(student__score__schedule_lesson__teacher__user=user).exclude(who_collect_me__user=user).order_by('?')[:20]
        else:
            return None


class SomeTeacherMaybeKnowView(mixins.ListModelMixin,viewsets.GenericViewSet):
    pagination_class = DefaultPagination
    permission_classes = (IsAuthenticated,)
    serializer_class = UserSerializer
    def get_queryset(self):
        user=self.request.user
        if user.is_student:
            return UserProfile.objects.filter(teacher__schedule_lesson__score__student__user=user).exclude(who_collect_me__user=user).order_by('?')[:20]
        elif user.is_teacher:
            return UserProfile.objects.filter(teacher__schedule_lesson__lesson__schedule_lesson__teacher__user=user).exclude(who_collect_me__user=user).order_by('?')[:20]
        else:
            return None