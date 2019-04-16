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
from users.views import StudentView,StudentDetailRetrieveView,TeacherView\
    # ,CaptchaView

from message.views import OutboxView,OutboxMessageFileView,MessageReceiverView,OutboxMessageGroupCreateView,\
    MessageGroupReceiverView,InboxReceiverMessageView,InboxGroupReceiverView

router=DefaultRouter()
router.register(r'student-schedule',StudentScheduleViewSet,basename='student-schedule')
router.register(r'schedule-student-list',ScoreStudentListViewSet,basename='student-list')
router.register(r'teacher-schedule',TeacherScheduleViewSet,basename='teahcer-schedule')
router.register(r'score',ScoreViewSet,basename='score')
router.register(r'total-credit',TotalCreditViewSet,basename='total-credit')
router.register(r'student',StudentView,basename='student')
router.register(r'student-detail-retrieve',StudentDetailRetrieveView,basename='student-detail-retrieve')
router.register(r'teacher',TeacherView,basename='teacher')
# router.register(r'login',obtain_jwt_token,basename='login')
# router.register(r'captcha-check',CaptchaView,basename='captcha-check')

router.register(r'outbox',OutboxView,basename='outbox')
router.register(r'outbox-message-file',OutboxMessageFileView,basename='outbox-message-file')
router.register(r'message-receiver',MessageReceiverView,basename='message-receiver')
router.register(r'outbox-message-group',OutboxMessageGroupCreateView,basename='outbox-message-group')
router.register(r'inbox-group-message-update',MessageGroupReceiverView,basename='inbox-group-message-update')
router.register(r'inbox-receiver-message',InboxReceiverMessageView,basename='inbox-receiver-message')
router.register(r'inbox-group-receiver-message',InboxGroupReceiverView,basename='inbox-group-receiver-message')

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
    url(r'^ckeditor/', include('ckeditor_uploader.urls')),
    # url(r'api/v1/captcha/', include('rest_captcha.urls')),
    # url(r'^api/v1/captcha-check/',CaptchaView.as_view(),name='captcha-check')
    # url(r'api/v1/group-list/',GroupList.as_view(),name='group-list')
    # url(r'^media/(?P<path>.*)$',serve,{'document_root':MEDIA_ROOT}),
]


# static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)



























