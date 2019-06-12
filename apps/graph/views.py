from django.shortcuts import render
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import ListModelMixin,CreateModelMixin
from rest_framework.views import APIView
from .serializers import FindRelationViewSerializer,FindUserChildNodeViewSerializer,FindMyLessonNodeViewSerializer\
    ,FindMyMajorNodeViewSerializer,FindSimilarMajorNodeViewSerializer,FindMajorLessonNodeViewSerializer

from rest_framework import status
from rest_framework.response import Response

# Create your views here.

class FindRelationView(GenericViewSet,CreateModelMixin):
    '''
    搜索A学生（老师） 和 B学生（老师）之间的关系，最短路径
    '''
    serializer_class = FindRelationViewSerializer
    def perform_create(self, serializer):
        return serializer.save()
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data=self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(data, status=status.HTTP_201_CREATED, headers=headers)


class FindUserChildNodeView(GenericViewSet,CreateModelMixin):
    '''
    分页查找一个用户节点的关系节点
    '''
    serializer_class = FindUserChildNodeViewSerializer
    def perform_create(self, serializer):
        return serializer.save()
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(data, status=status.HTTP_201_CREATED, headers=headers)


class FindMyLessonNodeView(GenericViewSet,CreateModelMixin):
    '''
    分页查找一个用户的课程关系节点
    '''
    serializer_class = FindMyLessonNodeViewSerializer
    def perform_create(self, serializer):
        return serializer.save()
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(data, status=status.HTTP_201_CREATED, headers=headers)



class FindMyMajorNodeView(GenericViewSet,CreateModelMixin):
    '''
        查找一个用户的专业
    '''
    serializer_class = FindMyMajorNodeViewSerializer
    def perform_create(self, serializer):
        return serializer.save()
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(data, status=status.HTTP_201_CREATED, headers=headers)



class FindSimilarMajorNodeView(GenericViewSet,CreateModelMixin):
    '''
        查找专业的相似专业
    '''
    serializer_class = FindSimilarMajorNodeViewSerializer
    def perform_create(self, serializer):
        return serializer.save()
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(data, status=status.HTTP_201_CREATED, headers=headers)


class FindMajorLessonNodeView(GenericViewSet,CreateModelMixin):
    '''
        查找专业的培养方案课程
    '''
    serializer_class = FindMajorLessonNodeViewSerializer
    def perform_create(self, serializer):
        return serializer.save()
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(data, status=status.HTTP_201_CREATED, headers=headers)




