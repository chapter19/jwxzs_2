#-*- coding:utf-8 -*-
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework.mixins import CreateModelMixin,RetrieveModelMixin
from rest_framework.response import Response
from rest_framework import status
from rest_framework import viewsets
from django.contrib.auth.hashers import make_password
from rest_framework import mixins
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework.pagination import PageNumberPagination
from django.contrib import auth

from spiders.student_dynamic import SpiderDynamicStudent
from spiders.teacher_dynamic import SpiderDynamicTeacher

from .models import Student,StudentDetail,Teacher
from .serializer import StudentSerializer,StudentDetailSerializer,TeacherSerializer,CatptchaSerializer
from .filters import StudentFilters,TeacherFilters
from rest_framework.views import APIView

User=get_user_model()

class DefaultPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    page_query_param = 'page'
    max_page_size = 100


class CustomBackend(ModelBackend):
    '''
    自定义用户认证
    '''
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user=User.objects.get(username=username)
            if user.check_password(password):
                return user
            else:
                return None
        except:
            lenth=len(username)
            if lenth==10 or lenth==12:
                dynamic_student=SpiderDynamicStudent(id=str(username),password=str(password))
                # dynamic_student.test()
                sign_in=dynamic_student.sign_in()
                if sign_in:
                    User.objects.create_user(username=username, password=password,is_student=True)
                    student_user=auth.authenticate(username=username, password=password)
                    # pw=make_password(password=password)
                    # studnet_user=User(username=username,password=pw,is_student=True)
                    # studnet_user.save()
                    dynamic_student.get_all_data()
                    return student_user
                else:
                    return None
            elif lenth==5 or lenth==6:
                dynamic_teacher=SpiderDynamicTeacher(id=str(username),password=str(password))
                sign_in=dynamic_teacher.sign_in()
                if sign_in:
                    User.objects.create_user(username=username, password=password, is_teacher=True)
                    teacher_user = auth.authenticate(username=username, password=password)
                    return teacher_user
                else:
                    return None
            else:
                return None
            # return None


class StudentView(mixins.ListModelMixin,RetrieveModelMixin,viewsets.GenericViewSet):
    queryset=Student.objects.all()
    pagination_class = DefaultPagination
    permission_classes = (IsAuthenticated,)
    serializer_class=StudentSerializer
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter,)
    filter_class = StudentFilters
    ordering_fields = ['id','name','cla__grade','cla__name','cla__colloge__name','gender']



class StudentDetailRetrieveView(RetrieveModelMixin,viewsets.GenericViewSet):
    # queryset = StudentDetail.objects.all()
    serializer_class = StudentDetailSerializer
    lookup_field ='base_data'
    def get_queryset(self):
        return StudentDetail.objects.filter(base_data__id=self.request.user.username)


class TeacherView(mixins.ListModelMixin,RetrieveModelMixin,viewsets.GenericViewSet):
    queryset = Teacher.objects.all()
    pagination_class = DefaultPagination
    permission_classes = (IsAuthenticated,)
    serializer_class = TeacherSerializer
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter,)
    filter_class = TeacherFilters
    ordering_fields = ['id', 'name','department__name','gender']

class CaptchaView(APIView):
    serializer_class =CatptchaSerializer

