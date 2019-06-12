#-*- coding:utf-8 -*-

from channels_api.bindings import ResourceBinding

from .models import TheCheck
from .serializers import TheCheckViewSerializer

class TheCheckBinding(ResourceBinding):

    model = TheCheck
    stream = "thecheck"
    serializer_class = TheCheckViewSerializer
    def get_queryset(self):
        return TheCheck.objects.filter(checked_student__student=self.request.user,time_limit__isnull=True)