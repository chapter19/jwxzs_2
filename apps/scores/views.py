# -*- coding: utf-8 -*-
from rest_framework import mixins
from rest_framework import viewsets
from .serializer import ScoreSerializer,ScoreStudentListSerializer,TotalCreditSerializer
from .models import Score,TotalCredit
from django_filters.rest_framework import DjangoFilterBackend
from .filters import ScoreFilter,ScoreStudentListFilter,TotalCreditFilter
from utils.permissions import StudentScoreIsOwnerOrReadOnly
from rest_framework.permissions import IsAuthenticated


class ScoreViewSet(mixins.ListModelMixin,viewsets.GenericViewSet):
    '''
    List:
        学生成绩接口
    '''
    queryset = Score.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class=ScoreSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_class=ScoreFilter

    def get_queryset(self):
        """
        This view should return a list of all the purchases
        for the currently authenticated user.
        """
        user = self.request.user
        return Score.objects.filter(student__id=user.username)


class ScoreStudentListViewSet(mixins.ListModelMixin,viewsets.GenericViewSet):
    queryset = Score.objects.all()
    permission_classes=(IsAuthenticated,)
    serializer_class = ScoreStudentListSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_class = ScoreStudentListFilter


class TotalCreditViewSet(mixins.ListModelMixin,viewsets.GenericViewSet):
    # queryset = TotalCredit.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = TotalCreditSerializer
    # filter_backends = (DjangoFilterBackend,)
    # filter_class=TotalCreditFilter
    def get_queryset(self):
        if self.request.user.is_student:
            return  TotalCredit.objects.filter(student__id=self.request.user.username)
        return None









