from django.shortcuts import render


from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet

from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework_extensions.cache.mixins import CacheResponseMixin
from rest_framework.response import Response
from rest_framework_extensions.cache.decorators import cache_response



from .models import Redio
from .serializers import RedioListSerializer,RedioRetrieveSerializer
from .filters import RedioFilter
from users.views import DefaultPagination

from .tasks import redio_retrieve_log,redio_list_log


class RedioView(CacheResponseMixin,mixins.ListModelMixin,mixins.RetrieveModelMixin,GenericViewSet):
    '''
    list:
        查看教务通知列表
    retrieve:
        查看教务通知详情
    '''
    pagination_class = DefaultPagination
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter,)
    filter_class = RedioFilter
    permission_classes = (IsAuthenticated,)
    ordering_fields = ['id','time','title']
    @cache_response(key_func='object_cache_key_func')
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        try:
            redio_retrieve_log.delay(request.META.get('REMOTE_ADDR'),request.user.id,self.kwargs.get('pk'))
        except:
            print('创建查询教务通知日志详情异常')
        return Response(serializer.data)

    @cache_response(key_func='list_cache_key_func')
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            try:
                redio_list_log.delay(request.META.get('REMOTE_ADDR'),request.user.id,request._request.GET.get('title',''),request._request.GET.get('time_range_after',''),request._request.GET.get('time_range_before',''))
            except:
                print('创建查询教务通知日志的参数异常')
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def get_serializer_class(self):
        if self.action=='list':
            return RedioListSerializer
        elif self.action=='retrieve':
            return RedioRetrieveSerializer
    def get_queryset(self):
        return Redio.objects.all()









