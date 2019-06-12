from django.shortcuts import render
from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import IsAuthenticated

from .models import TheCheck,CheckedStudent
from .serializers import TheCheckViewCreateSerializer,TheCheckViewSerializer,TheCheckViewUpdateSerializer\
    ,TeacherCheckedStudentListSerializer,StudentCheckedStudentListSerializer,StudentCheckedStudentUpdateSerializer
from groups.models import GroupAdministrator,Group
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from .filters import TheCheckFilter,CheckedStudentFilter
from users.views import DefaultPagination

from rest_framework import status
from rest_framework.response import Response

# Create your views here.


class TheCheckView(GenericViewSet,mixins.ListModelMixin,mixins.RetrieveModelMixin,mixins.DestroyModelMixin,mixins.UpdateModelMixin,mixins.CreateModelMixin):
    '''
    list:
        列出所有点到，加参数schedule_lesson={id}过滤单门课程班级的点到
    create:
        创建点到
    update：
        更新点到
    delete：
        删除点到
    read:
        点到详情
    '''
    permission_classes = (IsAuthenticated,)
    def get_serializer_class(self):
        if self.action=='create':
            return TheCheckViewCreateSerializer
        elif self.action=='update' or self.action=='partial_update':
            return TheCheckViewUpdateSerializer
        elif self.action=='list' or 'retrieve':
            return TheCheckViewSerializer
    def get_queryset(self):
        if self.action in ['create','destroy','update']:
            return TheCheck.objects.filter(promoter=self.request.user)
        elif self.action=='list' or self.action=='retrieve':
            if self.request.user.is_teacher:
                return TheCheck.objects.filter(promoter=self.request.user)
            elif self.request.user.is_student:
                return TheCheck.objects.filter(checked_student__student=self.request.user)
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter,)
    filter_class = TheCheckFilter
    pagination_class = DefaultPagination
    ordering_fields = ('start_time',)



class CheckedStudentView(GenericViewSet,mixins.ListModelMixin,mixins.RetrieveModelMixin,mixins.UpdateModelMixin):
    '''
    list:
        列出所有的点到学生，学生用于查询和自己相关的点到，教师用于查看点到名单情况
    update:
        学生改变自己的点到状态
    read:
        点到学生的详情
    '''
    permission_classes = (IsAuthenticated,)
    pagination_class = DefaultPagination
    def get_serializer_class(self):
        if self.action == 'update' or self.action == 'partial_update':
            return StudentCheckedStudentUpdateSerializer
        elif self.action=='list' or self.action=='retrieve':
            if self.request.user.is_student:
                return StudentCheckedStudentListSerializer
            elif self.request.user.is_teacher:
                return TeacherCheckedStudentListSerializer
    def get_queryset(self):
        if self.action=='update':
            return CheckedStudent.objects.filter(student=self.request.user)
        elif self.action=='list' or self.action=='retrieve':
            if self.request.user.is_teacher:
                return CheckedStudent.objects.filter(the_check__promoter=self.request.user)
            elif self.request.user.is_student:
                return CheckedStudent.objects.filter(student=self.request.user)
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter,)
    filter_class = CheckedStudentFilter
    ordering_fields = ('check_time',)






