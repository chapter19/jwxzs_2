# -*- coding: utf-8 -*-
from rest_framework import mixins
from rest_framework import viewsets
from .serializer import ScoreSerializer,ScoreStudentListSerializer,TotalCreditSerializer,ScoreSemesterSerializer,ScoreUpdateSerializer,NewScoreListSerializer,NewScoreUpdateSerializer
from .models import Score,TotalCredit,NewScore
from django_filters.rest_framework import DjangoFilterBackend
from .filters import ScoreFilter,ScoreStudentListFilter
from utils.permissions import StudentScoreIsOwnerOrReadOnly
from rest_framework.permissions import IsAuthenticated
from rest_framework import filters
from users.views import DefaultPagination
from django.db.models import Q

from rest_framework_extensions.cache.mixins import CacheResponseMixin
from rest_framework_extensions.cache.decorators import cache_response
from rest_framework.response import Response
from rest_framework import pagination
from rest_framework import status
from semesters.models import Semester


from users.views import DefaultPagination
from .tasks import student_scores_log,teacher_scores_log,student_total_credit_log,teacher_total_credit_log,schedule_student_list_log



class ScorePagination(pagination.PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    page_query_param = 'page'
    max_page_size = 100
    def get_paginated_response(self, data):
        semester_credit=0
        for d in data:
            semester_credit+=d['schedule_lesson']['lesson']['credit']
        return Response({
            'links': {
                'next': self.get_next_link(),
                'previous': self.get_previous_link()
            },
            'semester_credit':semester_credit,
            'count': self.page.paginator.count,
            'results': data
        })


class ScoreViewSet(CacheResponseMixin,mixins.ListModelMixin,viewsets.GenericViewSet):
    '''
    List:
        学生成绩接口
    '''
    # pagination_class = ScorePagination
    pagination_class = DefaultPagination
    queryset = Score.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class=ScoreSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_class=ScoreFilter
    @cache_response(key_func='list_cache_key_func')
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            try:
                if request.user.is_student:
                    student_scores_log.delay(request.META.get('REMOTE_ADDR'),request.user.id,request._request.GET.get('student_id', ''),request._request.GET.get('semester', ''),request._request.GET.get('if_major', ''))
                elif request.user.is_teacher:
                    teacher_scores_log.delay(request.META.get('REMOTE_ADDR'),request.user.id,request._request.GET.get('student_id', ''),request._request.GET.get('semester', ''),request._request.GET.get('if_major', ''))
            except:
                print('获取过滤学生成绩参数异常')
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    def get_queryset(self):
        if self.request.user.is_student:
            return Score.objects.filter(student__user=self.request.user)
        elif self.request.user.is_teacher:
            return Score.objects.all()



class ScoreStudentListViewSet(CacheResponseMixin,mixins.ListModelMixin,viewsets.GenericViewSet):
    pagination_class = DefaultPagination
    permission_classes=(IsAuthenticated,)
    serializer_class = ScoreStudentListSerializer
    filter_backends = (DjangoFilterBackend,filters.OrderingFilter,)
    filter_class = ScoreStudentListFilter
    ordering_fields=['student__id',]

    @cache_response(key_func='list_cache_key_func')
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            try:
                schedule_student_list_log.delay(request.META.get('REMOTE_ADDR'), request.user.id,request._request.GET.get('schedule_lesson_id', ''))
            except:
                print('获取查询学生列表日志参数异常')
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    def get_queryset(self):
        return Score.objects.all()


class TotalCreditViewSet(CacheResponseMixin,mixins.RetrieveModelMixin,viewsets.GenericViewSet):
    # queryset = TotalCredit.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = TotalCreditSerializer
    lookup_field = 'student'
    # filter_backends = (DjangoFilterBackend,)
    # filter_class=TotalCreditFilter

    @cache_response(key_func='object_cache_key_func')
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        try:
            if request.user.is_student:
                student_total_credit_log.delay(request.META.get('REMOTE_ADDR'),request.user.id,kwargs.get('student'))
            elif request.user.is_teacher:
                teacher_total_credit_log.delay(request.META.get('REMOTE_ADDR'), request.user.id, kwargs.get('student'))
        except:
            print('创建总学分详情日志失败')
        return Response(serializer.data)

    def get_queryset(self):
        if self.request.user.is_student:
            return  TotalCredit.objects.filter(student__user=self.request.user)
        elif self.request.user.is_teacher:
            return TotalCredit.objects.all()



class ScoreSemesterView(mixins.CreateModelMixin,viewsets.GenericViewSet):
    '''
    create:
        获取学生有成绩的所有学期
    '''
    permission_classes = (IsAuthenticated,)
    serializer_class = ScoreSemesterSerializer
    def perform_create(self, serializer):
        return serializer.save()
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(data, status=status.HTTP_201_CREATED, headers=headers)
    def get_queryset(self):
        return Semester.objects.all()


class UpdateScoreView(mixins.CreateModelMixin,viewsets.GenericViewSet):
    '''
    create:
        更新成绩
    '''
    permission_classes = (IsAuthenticated,)
    serializer_class = ScoreUpdateSerializer
    def perform_create(self, serializer):
        return serializer.save()
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(data, status=status.HTTP_201_CREATED, headers=headers)
    def get_queryset(self):
        return Score.objects.filter(student_id=self.request.user.username)

class NewScoreView(mixins.CreateModelMixin,mixins.ListModelMixin,viewsets.GenericViewSet):
    '''
    list:
        获取最新成绩
    create:
        更新最新成绩
    '''
    permission_classes = (IsAuthenticated,)
    def get_serializer_class(self):
        if self.action=='list':
            return NewScoreListSerializer
        else:
            return NewScoreUpdateSerializer
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(data, status=status.HTTP_201_CREATED, headers=headers)
    def perform_create(self, serializer):
        return serializer.save()
    def get_queryset(self):
        return NewScore.objects.filter(student_id=self.request.user.username)


# class SemesterView():
#     pass

