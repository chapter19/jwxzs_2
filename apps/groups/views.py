from django.shortcuts import render
from rest_framework import mixins
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .filters import GroupFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters


from .serializers import CreateDefGroupSerializer,UpdateDefGroupSerializer,CreateDefGroupMemberSerializer,RetrieveDefGroupSerializer,\
    ListGroupSerializer
from .models import DefGroup,DefGroupMember,Group,GroupAdministrator
from django.db.models import Q
from .permissions import CreateDefGroupMemberIsOwnerOrReadOnly
from users.views import DefaultPagination


class DefGroupView(mixins.CreateModelMixin,mixins.UpdateModelMixin,mixins.RetrieveModelMixin,viewsets.GenericViewSet):
    '''
    create:
        创建自定义组
    update:
        更新自定义组
    read:
        自定义组详情
    '''
    permission_classes = (IsAuthenticated,)
    def get_serializer_class(self):
        if self.action=='create':
            return CreateDefGroupSerializer
        elif self.action=='update':
            return UpdateDefGroupSerializer
        else:
            return RetrieveDefGroupSerializer
    def get_queryset(self):
        return DefGroup.objects.filter(creater=self.request.user)



class DefGroupMemberView(mixins.CreateModelMixin,mixins.DestroyModelMixin,viewsets.GenericViewSet):
    '''
    create:
        添加自定义组成员
    delete:
        移除自定义组成员
    '''
    def get_serializer_class(self):
        if self.action=='create':
            return CreateDefGroupMemberSerializer

    permission_classes = (IsAuthenticated,)
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.member==self.request.user or instance.def_group.creater==self.request.user:
            if instance.member!=instance.def_group.creater:
                self.perform_destroy(instance)
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                data={'detail':'你不可以退出自己创建的组！是否销毁该组？'}
                return Response(data,status=status.HTTP_403_FORBIDDEN)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)
    def get_queryset(self):
        if self.action=='create':
            return DefGroupMember.objects.filter(def_group__creater=self.request.user)
        else:
            return DefGroupMember.objects.filter(Q(def_group__creater=self.request.user)|Q(member=self.request.user))


class GroupView(mixins.ListModelMixin,mixins.RetrieveModelMixin,viewsets.GenericViewSet):
    '''
    list:
        组列表
    read:
        组详情
    '''
    permission_classes = (IsAuthenticated,)
    serializer_class = ListGroupSerializer
    pagination_class = DefaultPagination
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter,)
    filter_class = GroupFilter
    ordering_fields = ('group_id','group_type','group_name')
    def get_queryset(self):
        return Group.objects.filter(group_admin__admin=self.request.user)







