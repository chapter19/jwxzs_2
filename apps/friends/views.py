from django.shortcuts import render
from rest_framework import mixins
from rest_framework import viewsets
from .filters import CollectFriendsFilter,RecentContactFilter


from .models import CollectFriends
from .serializers import CollectFriendsSerializer,CreateCollectFriendsSerializer,RecentContactSerializer
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from .models import RecentContact
from users.views import DefaultPagination


class CollectFriendsView(mixins.ListModelMixin,mixins.CreateModelMixin,viewsets.GenericViewSet):
    '''
    list:
        收藏好友列表
    create:
        添加好友
    '''
    def get_queryset(self):
        return CollectFriends.objects.filter(user=self.request.user)
    def get_serializer_class(self):
        if self.action=='list':
            return CollectFriendsSerializer
        elif self.action=='create':
            return CreateCollectFriendsSerializer
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




