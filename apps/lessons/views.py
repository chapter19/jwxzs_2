# -*- coding: utf-8 -*-
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_extensions.cache.decorators import cache_response

from rest_framework import response

from .models import Schedule,ScheduleLesson,MajorLesson
from users.models import Student
from .serializer import ScheduleSerializers,StudentScheduleSemesterCountSerializer,TeacherScheduleSemesterCountSerializer,\
    MajorLessonSerializer,TeacherScheduleLessonSerializer
from rest_framework import status
from rest_framework import mixins
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from utils.permissions import StudentScheduleIsOwnerOrReadOnly

from django_filters.rest_framework import DjangoFilterBackend
from .filters import StudentScheduleFilter,TeacherScheduleFilter,MajorLessonFilter,TeacherScheduleLessonFilter,StudentScheduleLessonFilter
from scores.filters import ScoreFilter
from scores.models import Score
from rest_framework import filters

from rest_framework_extensions.cache.mixins import CacheResponseMixin

from users.views import DefaultPagination
from .tasks import student_schedule_log,teacher_schedule_log




class StudentScheduleViewSet(CacheResponseMixin,mixins.ListModelMixin,viewsets.GenericViewSet):
    '''
    学生课表接口
    '''
    pagination_class = DefaultPagination
    permission_classes = (IsAuthenticated,)
    serializer_class=ScheduleSerializers
    filter_backends = (DjangoFilterBackend,filters.OrderingFilter,)
    ordering_fields = ('counter','semester')
    filter_class = StudentScheduleFilter
    def get_queryset(self):
        return Schedule.objects.all()

    @cache_response(key_func='list_cache_key_func')
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            try:
                student_schedule_log.delay(request.META.get('REMOTE_ADDR'),request.user.id, request._request.GET.get('student_id', ''),request._request.GET.get('semester', ''),request.user.username)
            except:
                print('获取过滤学生课表参数异常')
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class TeacherScheduleViewSet(CacheResponseMixin,mixins.ListModelMixin,viewsets.GenericViewSet):
    '''
        教师课表接口
    '''
    pagination_class = DefaultPagination
    permission_classes = (IsAuthenticated,)
    serializer_class =ScheduleSerializers
    filter_backends = (DjangoFilterBackend,filters.OrderingFilter,)
    filter_class=TeacherScheduleFilter
    ordering_fields=('counter','semester')
    def get_queryset(self):
        return Schedule.objects.all()

    @cache_response(key_func='list_cache_key_func')
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            try:
                teacher_schedule_log.delay(request.META.get('REMOTE_ADDR'), request.user.id,
                                           request._request.GET.get('teacher_id', ''),
                                           request._request.GET.get('semester', ''), request.user.username)
            except:
                print('获取过滤学生课表参数异常')
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

# class ScheduleLessonStudentList(mixins.ListModelMixin,viewsets.GenericViewSet):
#     queryset = Score.objects.all()
#     serializer_class = StudentSerializer
#     filter_backends = (DjangoFilterBackend,)
#     filter_class=ScoreFilter


class StudentScheduleSemesterCountView(viewsets.GenericViewSet,mixins.CreateModelMixin):
    '''
    create:
        查看学生有课表的学期
    '''
    serializer_class = StudentScheduleSemesterCountSerializer
    permission_classes = (IsAuthenticated,)
    def perform_create(self, serializer):
        return serializer.save()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return response.Response(data, status=status.HTTP_201_CREATED, headers=headers)

    def get_queryset(self):
        return ScheduleLesson.objects.all()


class TeacherScheduleSemesterCountView(viewsets.GenericViewSet,mixins.CreateModelMixin):
    '''
    create:
        查看教师有课表的学期
    '''
    serializer_class = TeacherScheduleSemesterCountSerializer
    permission_classes = (IsAuthenticated,)
    def perform_create(self, serializer):
        return serializer.save()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return response.Response(data, status=status.HTTP_201_CREATED, headers=headers)

    def get_queryset(self):
        return ScheduleLesson.objects.all()


class MajorLessonView(viewsets.GenericViewSet,mixins.ListModelMixin):
    '''
    list:
        查看我的培养方案课程
    '''
    pagination_class = DefaultPagination
    permission_classes = (IsAuthenticated,)
    serializer_class = MajorLessonSerializer
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter,)
    ordering_fields = ('open_semester', )
    filter_class = MajorLessonFilter
    def get_queryset(self):
        return MajorLesson.objects.all()


class TeacherScheduleLessonView(mixins.ListModelMixin,viewsets.GenericViewSet):
    '''
    list:
        查看教师课程表课程列表
    '''
    pagination_class = DefaultPagination
    permission_classes = (IsAuthenticated,)
    serializer_class = TeacherScheduleLessonSerializer
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter,)
    # ordering_fields = ('',)
    filter_class = TeacherScheduleLessonFilter
    def get_queryset(self):
        return ScheduleLesson.objects.all()

class StudentScheduleLessonView(mixins.ListModelMixin,viewsets.GenericViewSet):
    '''
    list:
        查看学生课程表课程列表
    '''
    pagination_class = DefaultPagination
    permission_classes = (IsAuthenticated,)
    serializer_class = TeacherScheduleLessonSerializer
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter,)
    # ordering_fields = ('',)
    filter_class = StudentScheduleLessonFilter
    def get_queryset(self):
        return ScheduleLesson.objects.all()