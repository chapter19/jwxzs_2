# -*- coding: utf-8 -*-


from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Schedule
from users.models import Student
from .serializer import ScheduleSerializers
from rest_framework import status
from rest_framework import mixins
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from utils.permissions import StudentScheduleIsOwnerOrReadOnly

from django_filters.rest_framework import DjangoFilterBackend
from .filters import StudentScheduleFilter,TeacherScheduleFilter
from scores.filters import ScoreFilter
from scores.models import Score


# Create your views here.


class StudentScheduleViewSet(mixins.ListModelMixin,viewsets.GenericViewSet):
    # queryset=Schedule.objects.filter(schedule_lesson__score__student_id=request.user)
    queryset = Schedule.objects.all()
    permission_classes = (IsAuthenticated,StudentScheduleIsOwnerOrReadOnly,)
    serializer_class=ScheduleSerializers
    filter_backends = (DjangoFilterBackend,)
    filter_class = StudentScheduleFilter


class TeacherScheduleViewSet(mixins.ListModelMixin,viewsets.GenericViewSet):
    queryset = Schedule.objects.all()
    serializer_class =ScheduleSerializers
    filter_backends = (DjangoFilterBackend,)
    filter_class=TeacherScheduleFilter


# class ScheduleLessonStudentList(mixins.ListModelMixin,viewsets.GenericViewSet):
#     queryset = Score.objects.all()
#     serializer_class = StudentSerializer
#     filter_backends = (DjangoFilterBackend,)
#     filter_class=ScoreFilter





