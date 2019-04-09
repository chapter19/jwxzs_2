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
from users.views import StudentView,StudentDetailRetrieveView


router=DefaultRouter()
router.register(r'student-schedule',StudentScheduleViewSet,basename='student-schedule')
router.register(r'schedule-student-list',ScoreStudentListViewSet,basename='student-list')
router.register(r'teacher-schedule',TeacherScheduleViewSet,basename='teahcer-schedule')
router.register(r'score',ScoreViewSet,basename='score')
router.register(r'total-credit',TotalCreditViewSet,basename='total-credit')
router.register(r'student',StudentView,basename='student')
router.register(r'student-detail-retrieve',StudentDetailRetrieveView,basename='student-detail-retrieve')

urlpatterns = [
    url(r'^xadmin/', xadmin.site.urls),
    url(r'^media/(?P<path>.*)$',serve,{'document_root':MEDIA_ROOT}),
    # url(r'^api-token-auth/',views.obtain_auth_token),
    url(r'^api/v1/',include(router.urls)),
    # url(r'^api-auth/',include('rest_framework.urls',namespace='rest_framework')),
    #jwt认证接口
    url(r'^api/v1/login/', obtain_jwt_token),
    url(r'docs/',include_docs_urls(title=u'教务小助手')),
    url(r'^api-auth/', include('rest_framework.urls',namespace='rest_framework')),
]






























