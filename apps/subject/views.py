from rest_framework import mixins,viewsets,status,response
from rest_framework.permissions import IsAuthenticated
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend

from .serializers import PingJiaoListSerializer,PingJiaoCreateSerializer,XuankeListSerializers,\
    SynchronizeXuankeSerializer,DeleteXuankeSerializer,SetXuanDianSerializer,StepOneLessonTeacherSerializer,XuanKeSerializer

from users.models import MyPassword

from .models import PingJiaoTeacher,MyXuanKe,StepOneLessonTeacher
from semesters.models import NextSemester
from .filters import StepOneLessonTeacherFilter
from users.views import DefaultPagination


class PingJiaoListView(viewsets.GenericViewSet,mixins.CreateModelMixin):
    '''
    获取评教的老师名单列表
    '''
    permission_classes = (IsAuthenticated,)
    serializer_class = PingJiaoListSerializer
    def perform_create(self, serializer):
        return serializer.save()
    def create(self, request, *args, **kwargs):
        if self.request.user.is_student:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            data = self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return response.Response(data, status=status.HTTP_201_CREATED, headers=headers)
        else:
            return response.Response({'detail':'你不是学生，无法评教！'},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    def get_queryset(self):
        return PingJiaoTeacher.objects.filter(student_id=self.request.user.username)


class PingJiaoCreateView(viewsets.GenericViewSet,mixins.CreateModelMixin):
    '''
    一键评教
    '''
    serializer_class = PingJiaoCreateSerializer
    permission_classes = (IsAuthenticated,)
    def perform_create(self, serializer):
        return serializer.save()

    def create(self, request, *args, **kwargs):
        if self.request.user.is_student:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            data = self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return response.Response(data, status=status.HTTP_201_CREATED, headers=headers)
        else:
            return response.Response({'detail':'你不是学生，无法评教！'},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    def get_queryset(self):
        return PingJiaoTeacher.objects.filter(student_id=self.request.user.username)


class XuankeListView(viewsets.GenericViewSet,mixins.ListModelMixin):
    '''
    list:
        获取选课列表
    '''
    serializer_class = XuankeListSerializers
    permission_classes = (IsAuthenticated,)
    def get_queryset(self):
        if self.request.user.is_student:
            return MyXuanKe.objects.filter(student__user=self.request.user)
        else:
            return None


class SynchronizeXuankeView(viewsets.GenericViewSet,mixins.CreateModelMixin):
    serializer_class = SynchronizeXuankeSerializer
    permission_classes = (IsAuthenticated,)
    def perform_create(self, serializer):
        return serializer.save()
    def create(self, request, *args, **kwargs):
        if self.request.user.is_student:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            data = self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return response.Response(data, status=status.HTTP_201_CREATED, headers=headers)
        else:
            return response.Response({'detail':'你不是学生，无法同步选课！'},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    def get_queryset(self):
        return MyXuanKe.objects.filter(student__user=self.request.user)


class DeleteXuankeView(viewsets.GenericViewSet,mixins.CreateModelMixin):
    serializer_class = DeleteXuankeSerializer
    permission_classes = (IsAuthenticated,)
    def perform_create(self, serializer):
        return serializer.save()
    def create(self, request, *args, **kwargs):
        if self.request.user.is_student:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            data = self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return response.Response(data, status=status.HTTP_201_CREATED, headers=headers)
        else:
            return response.Response({'detail':'你不是学生，无法删除选课！'},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    def get_queryset(self):
        return MyXuanKe.objects.filter(student__user=self.request.user)


class SetXuanDianView(viewsets.GenericViewSet,mixins.CreateModelMixin):
    serializer_class = SetXuanDianSerializer
    permission_classes = (IsAuthenticated,)
    def perform_create(self, serializer):
        return serializer.save()
    def create(self, request, *args, **kwargs):
        if self.request.user.is_student:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            data = self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return response.Response(data, status=status.HTTP_201_CREATED, headers=headers)
        else:
            return response.Response({'detail':'你不是学生，无法设置选点！'},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    def get_queryset(self):
        return MyXuanKe.objects.filter(student__user=self.request.user)


class StepOneLessonTeacherView(viewsets.GenericViewSet,mixins.ListModelMixin):
    permission_classes = (IsAuthenticated,)
    pagination_class = DefaultPagination
    def get_queryset(self):
        next_semester=NextSemester.objects.first().next_semester
        return StepOneLessonTeacher.objects.filter(semester=next_semester)
    serializer_class = StepOneLessonTeacherSerializer

    filter_backends = (DjangoFilterBackend, filters.OrderingFilter,)
    ordering_fields = ('post_code',)
    filter_class = StepOneLessonTeacherFilter


class XuanKeView(viewsets.GenericViewSet,mixins.CreateModelMixin):
    serializer_class = XuanKeSerializer
    permission_classes = (IsAuthenticated,)
    def perform_create(self, serializer):
        return serializer.save()
    def create(self, request, *args, **kwargs):
        if self.request.user.is_student:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            data = self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return response.Response(data, status=status.HTTP_201_CREATED, headers=headers)
        else:
            return response.Response({'detail':'你不是学生，无法设置选点！'},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    def get_queryset(self):
        return MyXuanKe.objects.filter(student__user=self.request.user)