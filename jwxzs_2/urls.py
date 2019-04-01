# -*- coding=utf-8 -*-
"""jwxzs_2 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Import the include() function: from django.conf.urls import url, include
    3. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import url,include
import xadmin

from rest_framework.authtoken import views
from rest_framework_jwt.views import obtain_jwt_token,refresh_jwt_token

from jwxzs_2.settings import MEDIA_ROOT
from django.views.static import serve
from rest_framework.documentation import include_docs_urls
from rest_framework.routers import DefaultRouter

from lessons.views import StudentScheduleViewSet,TeacherScheduleViewSet
from scores.views import ScoreViewSet,ScoreStudentListViewSet,TotalCreditViewSet

router=DefaultRouter()
router.register(r'student_schedule',StudentScheduleViewSet,basename='student_schedule')
router.register(r'schedule_student_list',ScoreStudentListViewSet,basename='student_list')
router.register(r'teacher_schedule',TeacherScheduleViewSet,basename='teahcer_schedule')
router.register(r'score',ScoreViewSet,basename='score')
router.register(r'total_credit',TotalCreditViewSet,basename='total_credit')

urlpatterns = [
    url(r'^xadmin/', xadmin.site.urls),
    url(r'^media/(?P<path>.*)$',serve,{'document_root':MEDIA_ROOT}),
    # url(r'^api-token-auth/',views.obtain_auth_token),
    url(r'^',include(router.urls)),
    # url(r'^api-auth/',include('rest_framework.urls',namespace='rest_framework')),
    #jwt认证接口
    url(r'^login/', obtain_jwt_token),
    url(r'docs/',include_docs_urls(title=u'教务小助手')),
]






























