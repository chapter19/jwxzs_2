from django.shortcuts import render

from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet

from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters



from .models import Log
from .serializers import LogSerializer
from .filters import LogFilter
from users.views import DefaultPagination


class LogView(mixins.ListModelMixin,GenericViewSet):
    '''
    list:
        查看使用日志列表
    '''
    pagination_class = DefaultPagination
    serializer_class = LogSerializer
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter,)
    filter_class = LogFilter
    permission_classes = (IsAuthenticated,)
    ordering_fields = ['id','action_time','ip','action_type','address']
    def get_queryset(self):
        return Log.objects.filter(user=self.request.user)











