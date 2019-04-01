# -*- coding: utf-8 -*-
from rest_framework import mixins
from rest_framework import viewsets
from .serializer import ScoreSerializer,ScoreStudentListSerializer,TotalCreditSerializer
from .models import Score,TotalCredit
from django_filters.rest_framework import DjangoFilterBackend
from .filters import ScoreFilter,ScoreStudentListFilter,TotalCreditFilter
from utils.permissions import StudentScoreIsOwnerOrReadOnly
from rest_framework.permissions import IsAuthenticated

# Create your views here.

class ScoreViewSet(mixins.ListModelMixin,viewsets.GenericViewSet):
    queryset = Score.objects.all()
    permission_classes = (IsAuthenticated, StudentScoreIsOwnerOrReadOnly,)
    serializer_class=ScoreSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_class=ScoreFilter


class ScoreStudentListViewSet(mixins.ListModelMixin,viewsets.GenericViewSet):
    queryset = Score.objects.all()
    serializer_class = ScoreStudentListSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_class = ScoreStudentListFilter


class TotalCreditViewSet(mixins.ListModelMixin,mixins.DestroyModelMixin,viewsets.GenericViewSet):
    queryset = TotalCredit.objects.all()
    serializer_class = TotalCreditSerializer
    # filter_backends = (DjangoFilterBackend,)
    # filter_class=TotalCreditFilter









