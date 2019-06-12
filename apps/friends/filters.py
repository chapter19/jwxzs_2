#-*- coding:utf-8 -*-
import django_filters

from .models import CollectFriends,RecentContact


class CollectFriendsFilter(django_filters.rest_framework.FilterSet):
    friend_name=django_filters.CharFilter(field_name='friend__name',lookup_expr='icontains',help_text='好友姓名',label='好友姓名')
    friend_username=django_filters.CharFilter(field_name='friend__username',lookup_expr='exact',help_text='好友用户名',label='好友用户名')
    user_username=django_filters.CharFilter(field_name='user__username',lookup_expr='exact',help_text='用户用户名',label='用户用户名')
    class Meta:
        model=CollectFriends
        fields=['friend_name','friend_username','user_username']


class RecentContactFilter(django_filters.rest_framework.FilterSet):
    contact_name = django_filters.CharFilter(field_name='contact__name', lookup_expr='icontains', help_text='好友姓名')
    contact_username = django_filters.CharFilter(field_name='contact__username', lookup_expr='icontains',help_text='好友用户名(学号教号)')
    class Meta:
        model=RecentContact
        fields=['contact_name','contact_username']