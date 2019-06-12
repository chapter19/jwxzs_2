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

from lessons.views import StudentScheduleViewSet,TeacherScheduleViewSet,StudentScheduleSemesterCountView,\
    TeacherScheduleSemesterCountView,MajorLessonView,TeacherScheduleLessonView,StudentScheduleLessonView
from scores.views import ScoreViewSet,ScoreStudentListViewSet,TotalCreditViewSet,ScoreSemesterView,UpdateScoreView,NewScoreView
from users.views import StudentView,StudentDetailRetrieveView,TeacherView,StudentSearchView,ClassView,CollogeView,MajorView,DepartmentView,UserView,UpdatePasswordView,ResetPasswordView,UserProfileView
    # ,CaptchaView

from message.views import OutboxView,OutboxMessageFileView,MessageReceiverView,OutboxMessageGroupView,\
    InboxReceiverMessageView,InboxGroupReceiverView,ReceiverUpdateByQueryView,GroupReceiverUpdateByQueryView,\
    SenderUpdateByQueryView,OneKeyToReadView
from semesters.views import SemesterView,CurrentSemesterView
from groups.views import DefGroupView,GroupView,DefGroupMemberView,DefGroupListView
from friends.views import CollectFriendsView,RecentContactView,SomeStudentMaybeKnowView,SomeTeacherMaybeKnowView
from graph.views import FindRelationView,FindUserChildNodeView,FindMyLessonNodeView,FindMyMajorNodeView,FindSimilarMajorNodeView,FindMajorLessonNodeView
from checkstudent.views import TheCheckView,CheckedStudentView
from logs.views import LogView
from redio.views import RedioView
from subject.views import PingJiaoListView,PingJiaoCreateView,XuankeListView,SynchronizeXuankeView,DeleteXuankeView\
    ,SetXuanDianView,StepOneLessonTeacherView,XuanKeView
from homeworks.views import KnowledgeLabelView,UnitView,LessonPeriodView,HomeworkView,QuestionView,\
    QuestionImageView,ChoiceView,ChoiceTrueAnswerView,StudentChoiceAnswerView,PanDuanTrueAnswerView,\
    StudentPanDuanAnswerView,TianKongBlankView,TianKongTrueAnswerView,TianKongOtherAnswerView,StudentTianKongAnswerView,\
    JianDaAnswerView,StudentJianDaAnswerView,OtherAnswerImageView,OtherAnswerView,StudentOtherAnswerImageView,StudentOtherAnswerView,\
    DaiMaFileView,DaiMaAnswerView,StudentDaiMaAnswerView,HomeworkScoreView,QuestionScoreView,AutoCorrectNoSubmitHomeworkView
from disks.views import DiskView,DiskStatusView,DiskOpenView,FolderView,FileExtensionView,FileView,FileOpenView,FolderParentFolderUpdateView,FolderIfOpenUpdateView,FolderIfDeleteUpdateView,FolderCloneView,\
    FileCloneView,FileFolderUpdateView,LabelView,FolderPathView,OpenFolderPathView,DownloadFileView,ShareLinkView,SharelinkPasswordUpdateView,CheckedUserView,CheckedUserUpdateView

router=DefaultRouter()
router.register(r'student-schedule',StudentScheduleViewSet,basename='student-schedule')
router.register(r'major-lesson',MajorLessonView,basename='major-lesson')
router.register(r'student-schedule-semester',StudentScheduleSemesterCountView,basename='student-schedule-semester')
router.register(r'teacher-schedule-semester',TeacherScheduleSemesterCountView,basename='teacher-schedule-semester')
router.register(r'schedule-student-list',ScoreStudentListViewSet,basename='student-list')
router.register(r'teacher-schedule-lesson',TeacherScheduleLessonView,basename='teacher-schedule-lesson')
router.register(r'student-schedule-lesson',StudentScheduleLessonView,basename='student-schedule-lesson')
router.register(r'teacher-schedule',TeacherScheduleViewSet,basename='teahcer-schedule')
router.register(r'score',ScoreViewSet,basename='score')
router.register(r'total-credit',TotalCreditViewSet,basename='total-credit')
router.register(r'score-semester',ScoreSemesterView,basename='score-semester')
router.register(r'update-score',UpdateScoreView,basename='update-score')
router.register(r'new-score',NewScoreView,basename='new-score')


router.register(r'student',StudentView,basename='student')
router.register(r'student-detail-retrieve',StudentDetailRetrieveView,basename='student-detail-retrieve')
router.register(r'teacher',TeacherView,basename='teacher')
router.register(r'class',ClassView,basename='class')
router.register(r'colloge',CollogeView,basename='colloge')
router.register(r'major',MajorView,basename='major')
router.register(r'department',DepartmentView,basename='department')
router.register(r'user',UserView,basename='user')
router.register(r'user-profile',UserProfileView,basename='user-profile')
router.register(r'update-password',UpdatePasswordView,basename='update-password')
router.register(r'reset-password',ResetPasswordView,basename='reset-password')


# router.register(r'login',obtain_jwt_token,basename='login')
# router.register(r'captcha-check',CaptchaView,basename='captcha-check')

router.register(r'outbox',OutboxView,basename='outbox')
router.register(r'outbox-message-file',OutboxMessageFileView,basename='outbox-message-file')
router.register(r'message-receiver',MessageReceiverView,basename='message-receiver')
router.register(r'outbox-message-group',OutboxMessageGroupView,basename='outbox-message-group')
# router.register(r'inbox-group-update',MessageGroupReceiverView,basename='inbox-group-update')
router.register(r'inbox-receiver-message',InboxReceiverMessageView,basename='inbox-receiver-message')
router.register(r'inbox-group-receiver',InboxGroupReceiverView,basename='inbox-group-receiver')
router.register(r'receiver-update-by-query',ReceiverUpdateByQueryView,basename='receiver-update-by-query')
router.register(r'group-receiver-update-by-query',GroupReceiverUpdateByQueryView,basename='group-receiver-update-by-query')
router.register(r'sender-update-by-query',SenderUpdateByQueryView,basename='sender-update-by-query')
router.register(r'one-key-to-read',OneKeyToReadView,basename='one-key-to-read')


router.register(r'semester',SemesterView,basename='semester')
router.register(r'current-semester',CurrentSemesterView,basename='current-semester')
router.register(r'def-group',DefGroupView,basename='def-group')
router.register(r'def-group-member',DefGroupMemberView,basename='def-group-member')
router.register(r'def-group-list',DefGroupListView,basename='def-group-list')
router.register(r'group',GroupView,basename='group')

router.register(r'friend',CollectFriendsView,basename='friend')
router.register(r'recent-contact',RecentContactView,basename='recent-contact')
router.register(r'some-student-maybe-know',SomeStudentMaybeKnowView,basename='some-student-maybe-know')
router.register(r'some-teacher-maybe-know',SomeTeacherMaybeKnowView,basename='some-teacher-maybe-know')

router.register(r'find-relation',FindRelationView,basename='find-relation')
router.register(r'find-user-child-node',FindUserChildNodeView,basename='find-user-child-node')
router.register(r'find-my-lesson-node',FindMyLessonNodeView,basename='find-my-lesson-node')
router.register(r'find-my-major-node',FindMyMajorNodeView,basename='find-my-major-node')
router.register(r'find-similar-major-node',FindSimilarMajorNodeView,basename='find-similar-major-node')
router.register(r'find-major-lesson-node',FindMajorLessonNodeView,basename='find-major-lesson-node')
router.register(r'the-check',TheCheckView,basename='the-check')
router.register(r'check-student',CheckedStudentView,basename='check-student')
router.register(r'student-search',StudentSearchView,basename='student-search')
router.register(r'log',LogView,basename='log')
router.register(r'redio',RedioView,basename='redio')

router.register(r'pingjiao-list',PingJiaoListView,basename='pingjiao-list')
router.register(r'pingjiao-create',PingJiaoCreateView,basename='pingjiao-create')
router.register(r'xuanke-list',XuankeListView,basename='xuanke-list')
router.register(r'xuanke-synchronize',SynchronizeXuankeView,basename='xuanke-synchronize')
router.register(r'xuanke-delete',DeleteXuankeView,basename='xuanke-delete')
router.register(r'set-xuandian',SetXuanDianView,basename='set-xuandian')
router.register(r'xuanke-teacher-list',StepOneLessonTeacherView,basename='xuanke-teacher-list')
router.register(r'xuanke-create',XuanKeView,basename='xuanke-create')

# router.register(r'unit',UnitView,basename='unit')

router.register(r'disk',DiskView,basename='disk')
router.register(r'disk-status-update',DiskStatusView,basename='disk-status-update')
router.register(r'disk-open-update',DiskOpenView,basename='disk-open-update')
router.register(r'folder',FolderView,basename='folder')
router.register(r'folder-parent-folder-update',FolderParentFolderUpdateView,basename='folder-parent-folder-update')
router.register(r'folder-open-update',FolderIfOpenUpdateView,basename='folder-open-update')
router.register(r'folder-delete-update',FolderIfDeleteUpdateView,basename='folder-delete-update')
router.register(r'folder-clone',FolderCloneView,basename='folder-clone')
router.register(r'file-clone',FileCloneView,basename='file-clone')
router.register(r'file-extension',FileExtensionView,basename='file-extension')
router.register(r'file',FileView,basename='file')
router.register(r'file-open-update',FileOpenView,basename='file-open-update')
router.register(r'file-folder-update',FileFolderUpdateView,basename='file-folder-update')
router.register(r'label',LabelView,basename='label')
router.register(r'folder-path',FolderPathView,basename='folder-path')
router.register(r'open-folder-path',OpenFolderPathView,basename='open-folder-path')
router.register(r'download-file',DownloadFileView,basename='download-file')
router.register(r'sharelink',ShareLinkView,basename='sharelink')
router.register(r'sharelink-password-update',SharelinkPasswordUpdateView,basename='sharelink-password-update')
router.register(r'checked-user',CheckedUserView,basename='checked-user')
router.register(r'checked-user-update',CheckedUserUpdateView,basename='checked-user-update')

router.register(r'knowledge-label',KnowledgeLabelView,basename='knowledge-label')
router.register(r'unit',UnitView,basename='unit')
router.register(r'lesson-period',LessonPeriodView,basename='lesson-period')
router.register(r'homework',HomeworkView,basename='homework')
router.register(r'question',QuestionView,basename='question')
router.register(r'question-image',QuestionImageView,basename='question-image')
router.register(r'choice',ChoiceView,basename='choice')
router.register(r'student-choice-answer',StudentChoiceAnswerView,basename='student-choice-answer')
router.register(r'choice-true-answer',ChoiceTrueAnswerView,basename='choice-true-answer')
router.register(r'panduan-true-answer',PanDuanTrueAnswerView,basename='panduan-true-answer')
router.register(r'student-panduan-answer',StudentPanDuanAnswerView,basename='student-panduan-answer')
router.register(r'tiankong-blank',TianKongBlankView,basename='tiankong-blank')
router.register(r'tiankong-true-answer',TianKongTrueAnswerView,basename='tiankong-true-answer')
router.register(r'tiankong-other-answer',TianKongOtherAnswerView,basename='tiankong-other-answer')
router.register(r'student-tiankong-answer',StudentTianKongAnswerView,basename='student-tiankong-answer')
router.register(r'jianda-answer',JianDaAnswerView,basename='jianda-answer')
router.register(r'student-jianda-answer',StudentJianDaAnswerView,basename='student-jianda-answer')
router.register(r'other-answer-image',OtherAnswerImageView,basename='other-answer-image')
router.register(r'student-other-answer-image',StudentOtherAnswerImageView,basename='student-other-answer-image')
router.register(r'other-answer',OtherAnswerView,basename='other-answer')
router.register(r'student-other-answer',StudentOtherAnswerView,basename='student-other-answer')
router.register(r'daima-file',DaiMaFileView,basename='daima-file')
router.register(r'daima-answer',DaiMaAnswerView,basename='daima-answer')
router.register(r'student-daima-answer',StudentDaiMaAnswerView,basename='student-daima-answer')
router.register(r'homework-score',HomeworkScoreView,basename='homework-score')
router.register(r'question-score',QuestionScoreView,basename='question-score')
router.register(r'auto-correct-no-submit-homework',AutoCorrectNoSubmitHomeworkView,basename='auto-correct-no-submit-homework')


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
    url(r'^channels-api/', include('channels_api.urls')),
    url(r'^search/',include('haystack.urls')),
    # url(r'api/v1/captcha/', include('rest_captcha.urls')),
    # url(r'^api/v1/captcha-check/',CaptchaView.as_view(),name='captcha-check')
    # url(r'api/v1/group-list/',GroupList.as_view(),name='group-list')
    # url(r'^media/(?P<path>.*)$',serve,{'document_root':MEDIA_ROOT}),
]


# static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)



























