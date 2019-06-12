#-*- coding:utf-8 -*-
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework.response import Response
from rest_framework import viewsets
from django.contrib.auth.hashers import make_password
from rest_framework import mixins
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework.pagination import PageNumberPagination
from rest_framework_extensions.cache.decorators import cache_response

from utils.aes import make_my_password

from django.contrib import auth
from datetime import datetime

from spiders.student_dynamic import SpiderDynamicStudent
from spiders.teacher_dynamic import SpiderDynamicTeacher

from .models import Student,StudentDetail,Teacher,UserProfile,Class,Colloge,Major,Department,MyPassword
from .serializer import StudentSerializer,StudentDetailSerializer,TeacherSerializer,DepartmentSerializer,UserSerializer,ResetPasswordSerializer,UserProfileUpdateSerializer,UserProfileSerializer
    # ,CatptchaSerializer
from .filters import StudentFilters,TeacherFilters,ClassFilters,CollogeFilters,MajorFilter,DepartmentFilter,UserFilter
# from rest_framework.views import APIView
# User=get_user_model()
from drf_haystack.viewsets import HaystackViewSet
from .serializer import StudentSearchSerializer,ClassSerializer,CollogeSerializer,MajorSerializer,UpdatePasswordSerializer
from drf_haystack.filters import HaystackFilter, BaseHaystackFilterBackend

from .tasks import get_student_all_data,login_log,search_student_log,search_teacher_log,student_detail_log

from rest_framework_extensions.cache.mixins import CacheResponseMixin

from rest_framework.throttling import UserRateThrottle

from rest_framework.views import APIView
from utils.aes import make_my_password




def jwt_response_payload_handler(token, user=None, request=None):
    return {
        'token': token,
        'user': UserSerializer(user, context={'request': request}).data
    }



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
            user=UserProfile.objects.get(username=username)
            if user.is_active:
                if user.check_password(password):
                    return user
                else:
                    return None
            else:
                lenth = len(username)
                if lenth == 10 or lenth == 12:
                    dynamic_student = SpiderDynamicStudent(id=str(username), password=str(password))
                    sign_in = dynamic_student.sign_in()
                    if sign_in:
                        pw = make_password(password=password)
                        user.date_joined = datetime.now()
                        user.password=pw
                        user.is_active=True
                        user.save()
                        # my_password=make_my_password(password)
                        try:
                            MyPassword.objects.create(user_id=user.id,password=make_my_password(password))
                        except:
                            pass
                        get_student_all_data.delay(username)
                        return user
                    else:
                        return None
                elif lenth == 5 or lenth == 6:
                    dynamic_teacher = SpiderDynamicTeacher(id=str(username), password=str(password))
                    sign_in = dynamic_teacher.sign_in()
                    if sign_in:
                        pw = make_password(password=password)
                        user.date_joined=datetime.now()
                        user.password = pw
                        user.is_active = True
                        user.save()
                        try:
                            MyPassword.objects.create(user_id=user.id,password=make_my_password(password))
                        except:
                            pass
                        return user
                    else:
                        return None
                else:
                    return None
        except:
            return None


class StudentView(CacheResponseMixin,mixins.ListModelMixin,mixins.RetrieveModelMixin,viewsets.GenericViewSet):
    '''
    list:
        学生列表
    retrieve:
        学生详情
    '''
    throttle_classes = (UserRateThrottle,)
    pagination_class = DefaultPagination
    permission_classes = (IsAuthenticated,)
    serializer_class=StudentSerializer
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter,)
    filter_class = StudentFilters
    ordering_fields = ['id','name','cla__grade','cla__name','cla__colloge__name','gender']
    @cache_response(key_func='list_cache_key_func')
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            try:
                search_student_log.delay(request._request.GET.get('name', ''),request.META.get('REMOTE_ADDR'),request.user.id,request._request.GET.get('id',''),request._request.GET.get('gender',''),request._request.GET.get('grade',''),request._request.GET.get('colloge_id',''),request._request.GET.get('class_id',''))
            except:
                print('获取过滤学生参数异常')
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    def get_serializer_class(self):
        return StudentSerializer
    def get_queryset(self):
        return Student.objects.all()


class StudentDetailRetrieveView(CacheResponseMixin,mixins.RetrieveModelMixin,viewsets.GenericViewSet):
    '''
    retrieve:
        学生个人详细信息详情
    '''
    # queryset = StudentDetail.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = StudentDetailSerializer
    lookup_field ='base_data'
    @cache_response(key_func='object_cache_key_func')
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        try:
            student_detail_log.delay(request.META.get('REMOTE_ADDR'),request.user.id)
        except:
            print('学生详情日志异常')
        return Response(serializer.data)
    def get_queryset(self):
        return StudentDetail.objects.filter(base_data__id=self.request.user.username)


class TeacherView(CacheResponseMixin,mixins.ListModelMixin,mixins.RetrieveModelMixin,viewsets.GenericViewSet):
    '''
    list:
        教师列表
    retrieve:
        教师详情
    '''
    queryset = Teacher.objects.all()
    pagination_class = DefaultPagination
    permission_classes = (IsAuthenticated,)
    serializer_class = TeacherSerializer
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter,)
    filter_class = TeacherFilters
    ordering_fields = ['id', 'name','department__name','gender']

    @cache_response(key_func='list_cache_key_func')
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            try:
                search_teacher_log.delay(request.META.get('REMOTE_ADDR'),request.user.id, request._request.GET.get('name', ''), request._request.GET.get('gender', ''), request._request.GET.get('department_id',''),)
            except:
                print('获取过滤教师参数异常')
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

# class CaptchaView(APIView):
#     serializer_class =CatptchaSerializer


class StudentSearchView(HaystackViewSet):
    pagination_class = DefaultPagination
    index_models = [Student]
    serializer_class = StudentSearchSerializer
    filter_backends = [HaystackFilter]
    filter_fields = ("type",)
    queryset = Student.objects.all()


class ClassView(CacheResponseMixin,mixins.ListModelMixin,viewsets.GenericViewSet):
    '''
    list:
        班级列表
    '''
    permission_classes = (IsAuthenticated,)
    pagination_class = DefaultPagination
    serializer_class = ClassSerializer
    queryset = Class.objects.all()
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter,)
    filter_class = ClassFilters
    ordering_fields = ['id', 'name', 'grade']

class CollogeView(CacheResponseMixin,mixins.ListModelMixin,viewsets.GenericViewSet):
    '''
    list:
        学院列表
    '''
    permission_classes = (IsAuthenticated,)
    serializer_class = CollogeSerializer
    queryset = Colloge.objects.all()
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter,)
    filter_class = CollogeFilters
    ordering_fields = ['id','name']


class MajorView(CacheResponseMixin,mixins.ListModelMixin,viewsets.GenericViewSet):
    '''
    list:
        专业列表
    '''
    permission_classes = (IsAuthenticated,)
    pagination_class = DefaultPagination
    serializer_class = MajorSerializer
    queryset = Major.objects.all()
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter,)
    filter_class = MajorFilter
    ordering_fields = ['id', 'name','major_id','grade']


class DepartmentView(CacheResponseMixin,mixins.ListModelMixin,viewsets.GenericViewSet):
    '''
    list:
        老师部门列表
    '''
    permission_classes = (IsAuthenticated,)
    pagination_class = DefaultPagination
    serializer_class = DepartmentSerializer
    queryset = Department.objects.all()
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter,)
    filter_class = DepartmentFilter
    ordering_fields = ['id', 'name']


class UserView(mixins.ListModelMixin,mixins.RetrieveModelMixin,viewsets.GenericViewSet):
    '''
    list:
        用户信息列表
    retrieve:
        用户信息详情
    '''
    permission_classes = (IsAuthenticated,)
    serializer_class=UserSerializer
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter,)
    filter_class = UserFilter
    ordering_fields = ['id', 'name']
    def get_queryset(self):
        return UserProfile.objects.all()



class UpdatePasswordView(mixins.UpdateModelMixin,viewsets.GenericViewSet):
    '''
    update:
        更改密码
    partial update:
        部分更改密码
    '''
    permission_classes = (IsAuthenticated,)
    serializer_class = UpdatePasswordSerializer
    def get_queryset(self):
        return UserProfile.objects.filter(id=self.request.user.id)


class ResetPasswordView(mixins.CreateModelMixin,viewsets.GenericViewSet):
    '''
    create:
        重置密码
    '''
    serializer_class = ResetPasswordSerializer
    def get_queryset(self):
        return UserProfile.objects.all()


class UserProfileView(mixins.UpdateModelMixin,mixins.RetrieveModelMixin,viewsets.GenericViewSet):
    permission_classes = (IsAuthenticated,)
    def get_serializer_class(self):
        if self.action=='retrieve':
            return UserProfileSerializer
        else:
            return UserProfileUpdateSerializer
    def get_queryset(self):
        return UserProfile.objects.filter(id=self.request.user.id)










