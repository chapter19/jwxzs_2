from rest_framework import mixins
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from django.db.models import Q


from .serializers import CreateDefGroupSerializer,UpdateDefGroupSerializer,CreateDefGroupMemberSerializer,RetrieveDefGroupSerializer,\
    ListGroupSerializer,DefGroupMemberListSerializer
from .models import DefGroup,DefGroupMember,Group,GroupAdministrator
from django.db.models import Q
from .permissions import CreateDefGroupMemberIsOwnerOrReadOnly
from users.views import DefaultPagination
from .filters import GroupFilter


class DefGroupView(mixins.ListModelMixin,mixins.CreateModelMixin,mixins.UpdateModelMixin,mixins.RetrieveModelMixin,viewsets.GenericViewSet):
    '''
    create:
        创建自定义组
    update:
        更新自定义组
    read:
        自定义组详情
    '''
    permission_classes = (IsAuthenticated,)
    pagination_class = DefaultPagination
    def get_serializer_class(self):
        if self.action=='create':
            return CreateDefGroupSerializer
        elif self.action=='retrieve' or self.action=='list':
            return RetrieveDefGroupSerializer
        else:
            return UpdateDefGroupSerializer
    def get_queryset(self):
        return DefGroup.objects.filter(def_group_member__member=self.request.user)


class DefGroupListView(mixins.ListModelMixin,mixins.RetrieveModelMixin,viewsets.GenericViewSet):
    '''
    list:
        查看我所在的自定义组列表
    '''
    permission_classes = (IsAuthenticated,)
    serializer_class = RetrieveDefGroupSerializer
    pagination_class = DefaultPagination
    def get_queryset(self):
        return DefGroup.objects.filter(def_group_member__member=self.request.user)


class DefGroupMemberView(mixins.ListModelMixin,mixins.CreateModelMixin,mixins.DestroyModelMixin,viewsets.GenericViewSet):
    '''
    list:
        查看自定义组成员
    create:
        添加自定义组成员
    delete:
        移除自定义组成员
    '''
    def get_serializer_class(self):
        if self.action=='create':
            return CreateDefGroupMemberSerializer
        elif self.action=='list':
            return DefGroupMemberListSerializer
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
        elif self.action=='list':
            return DefGroupMember.objects.filter(member=self.request.user)
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
        return Group.objects.filter(Q(group_admin__admin=self.request.user)|Q(def_group__def_group_member__member=self.request.user))






