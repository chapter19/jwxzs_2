from django.shortcuts import render

from .models import Semester,CurrentSemester
from rest_framework import mixins,viewsets


from .serializers import SemesterSerializer,CurrentSemesterSerializer


from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from .filters import SemesterFilter

from users.views import DefaultPagination

class SemesterView(mixins.ListModelMixin,mixins.RetrieveModelMixin,viewsets.GenericViewSet):
    '''
    list:
        学期列表
    read:
        学期详情
    '''
    queryset = Semester.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = SemesterSerializer
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter,)
    filter_class = SemesterFilter
    # lookup_field = 'post_code'
    ordering_fields=['id','post_code']


class CurrentSemesterView(mixins.RetrieveModelMixin,viewsets.GenericViewSet):
    '''
    read:
        当前学期
    '''
    queryset = CurrentSemester.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = CurrentSemesterSerializer
    lookup_field = 'post_code'


