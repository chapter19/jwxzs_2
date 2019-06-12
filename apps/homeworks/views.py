from django.shortcuts import render
from rest_framework import mixins,viewsets,status,response
from rest_framework.permissions import IsAuthenticated
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from datetime import datetime,timedelta

from users.views import DefaultPagination
from .models import KnowledgeLabel,Unit,LessonPeriod,Homework,Question,QuestionImage,QuestionScore,\
    Choice,StudentChoiceAnswer,ChoiceTrueAnswer,HomeworkScore,PanDuanTrueAnswer,StudentPanDuanAnswer,\
    TianKongBlank,TianKongTrueAnswer,TianKongOtherAnswer,StudentTianKongAnswer,JianDaAnswer,StudentJianDaAnswer,\
    OtherAnswerImage,OtherAnswer,StudentOtherAnswerImage,StudentOtherAnswer,StudentDaiMaAnswer,DaiMaFile,DaiMaAnswer
from scores.models import Score
from .serializers import UnitList1Serializers,UnitCreateSerializers,UnitUpdateSerialiser,\
    KnowledgeLabelListSerializer,KnowledgeLabelCreateSerializer, \
    LessonPeriodListSerializer,LessonPeriodCreateSerializer,LessonPeriodUpdateSerializer,\
    HomeworkListSerializer,HomeworkCreateSerializer,HomeworkUpdateSerializer,\
    HomeworkScoreListSerializer,HomeworkScoreCreateSerializer,HomeworkScoreUpdateSerializer,\
    QuestionImageListSerializer,QuestionImageCreateSerializer,QuestionImageUpdateSerializer,\
    QuestionListSerializer,QuestionCreateSerializer,QuestionUpdateSerializer,\
    ChoiceListSerializer,ChoiceCreateSerializer,ChoiceUpdateSerializer,\
    StudentChoiceAnswerListSerializer,StudnetChoiceAnswerCreateSerializer,StudentChoiceAnswerUpdateSerializer,\
    ChoiceTrueAnswerListSerializer,ChoiceTrueAnswerCreateSerializer,ChoiceTrueAnswerUpdateSerializer,\
    PanDuanTrueAnswerListSerializer,PanDuanTrueAnswerCreateSerializer,PanDuanTrueAnswerUpdateSerializer,\
    StudentPanDuanAnswerCreateSerializer,StudentPanDuanAnswerListSerializer,StudentPanDuanAnswerUpdateSerializer,\
    TianKongBlankListSerializer,TianKongBlankUpdateSerializer,\
    TianKongTrueAnswerListSerializer,TianKongTrueAnswerCreateSerializer,TianKongTrueAnswerUpdateSerializer,\
    TianKongOtherAnswerListSerializer,TianKongOtherAnswerCreateSerializer,TianKongOtherAnswerUpdateSerializer,\
    StudentTianKongAnswerListSerializer,StudentTianKongAnswerCreateSerializer,StudentTianKongAnswerUpdateSerializer,\
    JianDaAnswerListSerializer,JianDaAnswerCreateSerializer,JianDaAnswerUpdateSerializer,\
    StudentJianDaAnswerListSerializer,StudentJianDaAnswerCreateSerializer,StudentJianDaAnswerUpdateSerializer,\
    OtherAnswerImageCreateSerializer,OtherAnswerImageUpdateSerializer,\
    OtherAnswerListSerializer,OtherAnswerCreateSerializer,OtherAnswerUpdateSerializer,\
    StudentOtherAnswerImageUpdateSerializer,StudentOtherAnswerImageCreateSerializer,\
    StudentOtherAnswerListSerializer,StudentOtherAnswerCreateSerializer,StudentOtherAnswerUpdateSerializer,\
    DaiMaFileListSerializer,DaiMaFileCreateSerializer,DaiMaFileUpdateSerializer,\
    DaiMaAnswerListSerializer,DaiMaAnswerCreateSerializer,DaiMaAnswerUpdateSerializer,\
    StudentDaiMaAnswerListSerializer,StudentDaiMaAnswerCreateSerializer,StudentDaiMaAnswerUpdateSerializer,\
    QuestionScoreListSerializer,QuestionScoreCreateSerializer,QuestionScoreUpdateSerializer,\
    AutoCorrectNoSubmitHomeworkSerialier

from .filters import KnowledgeLabelFilter,UnitFilter,LessonPeriodFilter,HomeworkFilter,QuestionFilter,\
    QuestionImageFilter,ChoiceFilter,StudentChoiceAnswerFilter,ChoiceTrueAnswerFilter,PanDuanTrueAnswerFilter,\
    StudentPanDuanAnswerFilter,TianKongBlankFilter,TianKongTrueAnswerFilter,TianKongOtherAnswerFilter,StudentTianKongAnswerFilter,\
    JianDaAnswerViewFilter,StudentJianDaAnswerFilter,OtherAnswerFilter,StudentOtherAnswerFilter,DaiMaFileFilter,DaiMaAnswerFilter,\
    StudentDaiMaAnswerFilter,QuestionScoreFilter,HomeworkScoreFilter
from .tasks import auto_correct,auto_correct_no_submit_homework


class KnowledgeLabelView(mixins.ListModelMixin,mixins.CreateModelMixin,viewsets.GenericViewSet):
    '''
    list:
        知识点标签列表
    create:
        创建知识点标签
    '''
    pagination_class = DefaultPagination
    permission_classes = (IsAuthenticated,)
    filter_backends = (DjangoFilterBackend,filters.OrderingFilter)
    filter_class=KnowledgeLabelFilter
    def get_serializer_class(self):
        if self.action=='create':
            return KnowledgeLabelCreateSerializer
        else:
            return KnowledgeLabelListSerializer
    def get_queryset(self):
        return KnowledgeLabel.objects.all()


class UnitView(mixins.ListModelMixin,mixins.RetrieveModelMixin,mixins.CreateModelMixin,mixins.UpdateModelMixin,mixins.DestroyModelMixin,viewsets.GenericViewSet):
    '''
    list:
        课程章节列表
    create:
        创建课程章节
    update:
        更新课程章节
    partial_update:
        部分更新课程章节
    read:
        课程章节详情
    destroy:
        删除课程章节
    '''
    pagination_class = DefaultPagination
    permission_classes = (IsAuthenticated,)
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    filter_class = UnitFilter
    ordering_fields=('num','semester')
    def get_serializer_class(self):
        if self.action=='list' or self.action=='retrieve':
            return UnitList1Serializers
        if self.action=='create':
            return UnitCreateSerializers
        else:
            return UnitUpdateSerialiser
    def get_queryset(self):
        return Unit.objects.all()
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if self.request.user!=instance.create_user:
            return response.Response(status=status.HTTP_403_FORBIDDEN)
        if instance.unit_type==3:
            pass
        elif instance.unit_type==2:
            Unit.objects.filter(parent_unit=instance).delete()
        elif instance.unit_type==1:
            sub=Unit.objects.filter(parent_unit=instance)
            for s in sub:
                Unit.objects.filter(parent_unit=s).delete()
            sub.delete()
        self.perform_destroy(instance)
        return response.Response(status=status.HTTP_204_NO_CONTENT)
    def perform_destroy(self, instance):
        instance.delete()


class LessonPeriodView(mixins.CreateModelMixin,mixins.ListModelMixin,mixins.RetrieveModelMixin,mixins.UpdateModelMixin,mixins.DestroyModelMixin,viewsets.GenericViewSet):
    '''
    list:
        课时列表
    create:
        创建课时
    update:
        更新课时
    partial_update:
        部分更新课时
    destroy:
        删除课时
    read:
        课时详情
    '''
    pagination_class = DefaultPagination
    permission_classes = (IsAuthenticated,)
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    filter_class = LessonPeriodFilter
    ordering_fields = ('time',)
    def get_serializer_class(self):
        if self.action=='list' or self.action=='retrieve':
            return LessonPeriodListSerializer
        elif self.action=='create':
            return LessonPeriodCreateSerializer
        else:
            return LessonPeriodUpdateSerializer
    def get_queryset(self):
        return LessonPeriod.objects.all()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        user=self.request.user
        if not user.if_teacher:
            return response.Response(status=status.HTTP_403_FORBIDDEN)
        teacher=user.teacher
        if teacher!=instance.schedule_lesson.teacher:
            return response.Response(status=status.HTTP_403_FORBIDDEN)
        self.perform_destroy(instance)
        return response.Response(status=status.HTTP_204_NO_CONTENT)
    def perform_destroy(self, instance):
        instance.delete()


class HomeworkView(mixins.CreateModelMixin,mixins.ListModelMixin,mixins.RetrieveModelMixin,mixins.UpdateModelMixin,mixins.DestroyModelMixin,viewsets.GenericViewSet):
    '''
    list:
        作业列表
    create:
        创建作业
    update:
        更新作业
    partial_update:
        部分更新作业
    destroy:
        删除作业
    read:
        作业详情
    '''
    pagination_class = DefaultPagination
    permission_classes = (IsAuthenticated,)
    filter_backends = (DjangoFilterBackend,filters.OrderingFilter)
    filter_class=HomeworkFilter
    ordering_fields=('lesson_period__time')
    def get_serializer_class(self):
        if self.action=='list' or self.action=='retrieve':
            return HomeworkListSerializer
        elif self.action=='create':
            return HomeworkCreateSerializer
        else:
            return HomeworkUpdateSerializer
    def get_queryset(self):
        return Homework.objects.all()
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        user=self.request.user
        if not user.if_teacher:
            return response.Response(status=status.HTTP_403_FORBIDDEN)
        teacher=user.teacher
        if teacher!=instance.lesson_period.schedule_lesson.teacher:
            return response.Response(status=status.HTTP_403_FORBIDDEN)
        self.perform_destroy(instance)
        return response.Response(status=status.HTTP_204_NO_CONTENT)
    def perform_destroy(self, instance):
        instance.delete()


class HomeworkScoreView(mixins.CreateModelMixin,mixins.ListModelMixin,mixins.RetrieveModelMixin,mixins.UpdateModelMixin,viewsets.GenericViewSet):
    '''
    list:
        学生作业成绩列表
    create:
        创建初始化学生作业成绩
    update:
        更新学生作业成绩
    partial_update:
        部分更新学生作业成绩
    read:
        作业详情
    '''
    pagination_class = DefaultPagination
    permission_classes = (IsAuthenticated,)
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    filter_class = HomeworkScoreFilter
    ordering_fields = ('student','homework','create_time',)
    def get_serializer_class(self):
        if self.action=='list' or self.action=='retrieve':
            return HomeworkScoreListSerializer
        elif self.action=='create':
            return HomeworkScoreCreateSerializer
        else:
            return HomeworkScoreUpdateSerializer
    def get_queryset(self):
        user=self.request.user
        if user.is_teacher:
            return HomeworkScore.objects.all()
        elif user.is_student:
            return HomeworkScore.objects.filter(student=user.student)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        if instance.if_submit:
            return response.Response(status=status.HTTP_403_FORBIDDEN)
        user=self.request.user
        if not user.is_student:
            return response.Response(status=status.HTTP_403_FORBIDDEN)
        data=request.data
        serializer = self.get_serializer(instance, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}
        try:
            data=data.dict()
            if_submit = data['if_submit']
            if if_submit == True:
                auto_correct.delay(homework_id=instance.homework.id,student_id=user.student.id)
        except:
            pass
        return response.Response(serializer.data)

    def perform_update(self, serializer):
        serializer.save()

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)


class QuestionImageView(mixins.ListModelMixin,mixins.CreateModelMixin,mixins.UpdateModelMixin,mixins.DestroyModelMixin,viewsets.GenericViewSet):
    '''
    list:
        题目图片列表
    create:
        创建题目图片
    update:
        更新题目图片
    partial_update:
        部分更新题目图片
    destroy:
        删除题目图片
    read:
        作业详情
    '''
    pagination_class = DefaultPagination
    permission_classes = (IsAuthenticated,)
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    filter_class = QuestionImageFilter
    ordering_fields = ('number',)
    def get_serializer_class(self):
        if self.action=='list':
            return QuestionImageListSerializer
        elif self.action=='create':
            return QuestionImageCreateSerializer
        else:
            return QuestionImageUpdateSerializer
    def get_queryset(self):
        return QuestionImage.objects.all()

    def destroy(self, request, *args, **kwargs):
        user=self.request.user
        if not user.is_teacher:
            return response.Response(status=status.HTTP_403_FORBIDDEN)
        instance = self.get_object()
        question=instance.question
        if question.homework.lesson_period.schedule_lesson.teacher!=user.teacher:
            return response.Response(status=status.HTTP_403_FORBIDDEN)
        self.perform_destroy(instance)
        question.image_count-=1
        question.save()
        return response.Response(status=status.HTTP_204_NO_CONTENT)

    def perform_destroy(self, instance):
        instance.delete()


class QuestionView(mixins.CreateModelMixin,mixins.ListModelMixin,mixins.RetrieveModelMixin,mixins.DestroyModelMixin,mixins.UpdateModelMixin,viewsets.GenericViewSet):
    '''
    list:
        题目列表
    create:
        创建题目
    update:
        更新题目
    partial_update:
        部分更新题目
    destroy:
        删除题目
    read:
        题目详情
    '''
    pagination_class = DefaultPagination
    permission_classes = (IsAuthenticated,)
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    filter_class = QuestionFilter
    ordering_fields = ('number',)
    def get_serializer_class(self):
        if self.action=='list' or self.action=='retrieve':
            return QuestionListSerializer
        elif self.action=='create':
            return QuestionCreateSerializer
        else:
            return QuestionUpdateSerializer
    def get_queryset(self):
        return Question.objects.all()
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        user=self.request.user
        if not user.if_teacher:
            return response.Response(status=status.HTTP_403_FORBIDDEN)
        teacher=user.teacher
        if teacher!=instance.homework.lesson_period.schedule_lesson.teacher:
            return response.Response(status=status.HTTP_403_FORBIDDEN)
        homework=instance.homework
        homework.total_score -=instance.score
        homework.question_counter-=1
        self.perform_destroy(instance)
        homework.save()
        return response.Response(status=status.HTTP_204_NO_CONTENT)
    def perform_destroy(self, instance):
        instance.delete()


class ChoiceView(mixins.CreateModelMixin,mixins.ListModelMixin,mixins.UpdateModelMixin,mixins.DestroyModelMixin,mixins.RetrieveModelMixin,viewsets.GenericViewSet):
    '''
    list:
        选项列表
    create:
        创建选项
    update:
        更新选项
    partial_update:
        部分更新选项
    destroy:
        删除选项
    read:
        选项详情
    '''
    pagination_class = DefaultPagination
    permission_classes = (IsAuthenticated,)
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    filter_class = ChoiceFilter
    # ordering_fields = ('',)
    def get_serializer_class(self):
        if self.action=='list' or self.action=='retrieve':
            return ChoiceListSerializer
        elif self.action=='create':
            return ChoiceCreateSerializer
        else:
            return ChoiceUpdateSerializer
    def get_queryset(self):
        return Choice.objects.all()
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        user=self.request.user
        if not user.is_teacher:
            return response.Response(status=status.HTTP_403_FORBIDDEN)
        teacher=user.teacher
        if instance.question.homework.lesson_period.schedule_lesson.teacher!=teacher:
            return response.Response(status=status.HTTP_403_FORBIDDEN)
        self.perform_destroy(instance)
        return response.Response(status=status.HTTP_204_NO_CONTENT)
    def perform_destroy(self, instance):
        instance.delete()


class StudentChoiceAnswerView(mixins.CreateModelMixin,mixins.ListModelMixin,mixins.UpdateModelMixin,mixins.DestroyModelMixin,viewsets.GenericViewSet):
    '''
    list:
        学生选项列表
    create:
        创建学生选项
    update:
        更新学生选项
    partial_update:
        部分更新学生选项
    destroy:
        删除学生选项
    '''
    pagination_class = DefaultPagination
    permission_classes = (IsAuthenticated,)
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    filter_class = StudentChoiceAnswerFilter
    # ordering_fields = ('',)
    def get_serializer_class(self):
        if self.action=='list':
            return StudentChoiceAnswerListSerializer
        elif self.action=='create':
            return StudnetChoiceAnswerCreateSerializer
        else:
            return StudentChoiceAnswerUpdateSerializer
    def get_queryset(self):
        user=self.request.user
        if user.is_student:
            return StudentChoiceAnswer.objects.filter(student__user=self.request.user)
        elif user.is_teacher:
            return StudentChoiceAnswer.objects.all()
        else:
            return None
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        user=self.request.user
        if not user.is_student:
            return response.Response(status=status.HTTP_403_FORBIDDEN)
        student=user.student
        if student!=instance.student:
            return response.Response(status=status.HTTP_403_FORBIDDEN)
        homework=instance.question.homework
        if homework.limit_time<datetime.now():
            return response.Response(status=status.HTTP_403_FORBIDDEN)
        homework_score=HomeworkScore.objects.filter(homework=instance.question.homework,student=student)
        if homework_score:
            homework_score=homework_score[0]
            if homework_score.if_submit:
                return response.Response(status=status.HTTP_403_FORBIDDEN)
            else:
                timeout=instance.question.homework.timeout
                if timeout:
                    over_time=timedelta(minutes=timeout)+homework_score.create_time
                    if over_time<datetime.now():
                        return response.Response(status=status.HTTP_403_FORBIDDEN)
        else:
            return response.Response(status=status.HTTP_403_FORBIDDEN)
        self.perform_destroy(instance)
        return response.Response(status=status.HTTP_204_NO_CONTENT)
    def perform_destroy(self, instance):
        instance.delete()


class ChoiceTrueAnswerView(mixins.CreateModelMixin,mixins.ListModelMixin,mixins.UpdateModelMixin,mixins.DestroyModelMixin,viewsets.GenericViewSet):
    '''
    list:
        正确选项列表
    create:
        创建正确选项
    update:
        更新正确选项
    partial_update:
        部分更新正确选项
    destroy:
        删除正确选项
    '''
    pagination_class = DefaultPagination
    permission_classes = (IsAuthenticated,)
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    filter_class = ChoiceTrueAnswerFilter
    def get_serializer_class(self):
        if self.action=='list':
            return ChoiceTrueAnswerListSerializer
        elif self.action=='create':
            return ChoiceTrueAnswerCreateSerializer
        else:
            return ChoiceTrueAnswerUpdateSerializer
    def get_queryset(self):
        user=self.request.user
        if user.is_student:
            student=user.student
            return ChoiceTrueAnswer.objects.filter(question__homework__limit_time__lt=datetime.now())
        elif user.is_teacher:
            return ChoiceTrueAnswer.objects.filter(question__homework__lesson_period__schedule_lesson__teacher=user.teacher)
        else:
            return None
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        user=self.request.user
        if not user.is_teacher:
            return response.Response(status=status.HTTP_403_FORBIDDEN)
        teacher=user.teacher
        if instance.question.homework.lesson_period.schedule_lesson.teacher!=teacher:
            return response.Response(status=status.HTTP_403_FORBIDDEN)
        self.perform_destroy(instance)
        return response.Response(status=status.HTTP_204_NO_CONTENT)
    def perform_destroy(self, instance):
        instance.delete()


class PanDuanTrueAnswerView(mixins.CreateModelMixin,mixins.UpdateModelMixin,mixins.ListModelMixin,viewsets.GenericViewSet):
    '''
    list:
        查看判断题正确答案
    create:
        创建判断题正确答案
    update:
        更改判断题正确答案
    partial_update:
        部分更改判断题正确答案
    '''
    pagination_class = DefaultPagination
    permission_classes = (IsAuthenticated,)
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    filter_class = PanDuanTrueAnswerFilter
    def get_serializer_class(self):
        if self.action=='list':
            return PanDuanTrueAnswerListSerializer
        elif self.action=='create':
            return PanDuanTrueAnswerCreateSerializer
        else:
            return PanDuanTrueAnswerUpdateSerializer
    def get_queryset(self):
        user=self.request.user
        if user.is_student:
            student=user.student
            return PanDuanTrueAnswer.objects.filter(question__homework__limit_time__lt=datetime.now())
        elif user.is_teacher:
            return PanDuanTrueAnswer.objects.filter(question__homework__lesson_period__schedule_lesson__teacher=user.teacher)
        else:
            return None


class StudentPanDuanAnswerView(mixins.CreateModelMixin,mixins.UpdateModelMixin,mixins.ListModelMixin,viewsets.GenericViewSet):
    '''
    list:
        查看学生判断题答案
    create:
        学生创建判断题答案
    update:
        学生更改判断题答案
    partial_update:
        学生部分更改判断题答案
    '''
    pagination_class = DefaultPagination
    permission_classes = (IsAuthenticated,)
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    filter_class = StudentPanDuanAnswerFilter
    ordering_fields = ('update_time','student')
    def get_serializer_class(self):
        if self.action=='list':
            return StudentPanDuanAnswerListSerializer
        elif self.action=='create':
            return StudentPanDuanAnswerCreateSerializer
        else:
            return StudentPanDuanAnswerUpdateSerializer
    def get_queryset(self):
        user = self.request.user
        if user.is_student:
            return StudentPanDuanAnswer.objects.filter(student__user=self.request.user)
        elif user.is_teacher:
            return StudentPanDuanAnswer.objects.all()
        else:
            return None

class TianKongBlankView(mixins.ListModelMixin,mixins.UpdateModelMixin,viewsets.GenericViewSet):
    '''
    list:
        查看填空题空白的列表
    update:
        更改填空题空白
    partial_update:
        学生部分更改填空题空白
    '''
    pagination_class = DefaultPagination
    permission_classes = (IsAuthenticated,)
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    filter_class = TianKongBlankFilter
    def get_serializer_class(self):
        if self.action=='list':
            return TianKongBlankListSerializer
        else:
            return TianKongBlankUpdateSerializer
    def get_queryset(self):
        return TianKongBlank.objects.all()

class TianKongTrueAnswerView(mixins.ListModelMixin,mixins.CreateModelMixin,mixins.UpdateModelMixin,viewsets.GenericViewSet):
    '''
    list:
        填空题空的正确答案列表
    create:
        创建填空题空的正确答案
    update:
        更改填空题空的正确答案
    partial_update:
        部分更新填空题空的正确答案
    '''
    pagination_class = DefaultPagination
    permission_classes = (IsAuthenticated,)
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    filter_class = TianKongTrueAnswerFilter
    ordering_fields=('blank__number',)
    def get_serializer_class(self):
        if self.action=='list':
            return TianKongTrueAnswerListSerializer
        elif self.action=='create':
            return TianKongTrueAnswerCreateSerializer
        else:
            return TianKongTrueAnswerUpdateSerializer
    def get_queryset(self):
        user = self.request.user
        if user.is_student:
            student = user.student
            return TianKongTrueAnswer.objects.filter(blank__question__homework__limit_time__lt=datetime.now())
        elif user.is_teacher:
            return TianKongTrueAnswer.objects.all()
        else:
            return None


class TianKongOtherAnswerView(mixins.CreateModelMixin,mixins.RetrieveModelMixin,mixins.ListModelMixin,mixins.UpdateModelMixin,mixins.DestroyModelMixin,viewsets.GenericViewSet):
    '''
    list:
        填空其他答案列表
    create:
        创建填空其他答案
    update:
        更改填空其他答案
    partial_update:
        部分更改填空其他答案
    destroy:
        删除填空其他答案
    '''
    pagination_class = DefaultPagination
    permission_classes = (IsAuthenticated,)
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    filter_class = TianKongOtherAnswerFilter
    ordering_fields = ('blank__number',)
    def get_serializer_class(self):
        if self.action=='list' or self.action=='retrieve':
            return TianKongOtherAnswerListSerializer
        elif self.action=='create':
            return TianKongOtherAnswerCreateSerializer
        else:
            return TianKongOtherAnswerUpdateSerializer
    def get_queryset(self):
        user = self.request.user
        if user.is_student:
            # student = user.student
            return TianKongOtherAnswer.objects.filter(blank__question__homework__limit_time__lt=datetime.now())
        elif user.is_teacher:
            return TianKongOtherAnswer.objects.all()
        else:
            return None
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        user=self.request.user
        if not user.is_teacher:
            return response.Response(status=status.HTTP_403_FORBIDDEN)
        teacher=user.teacher
        if instance.blank.question.homework.lesson_period.schedule_lesson.teacher!=teacher:
            return response.Response(status=status.HTTP_403_FORBIDDEN)
        self.perform_destroy(instance)
        return response.Response(status=status.HTTP_204_NO_CONTENT)
    def perform_destroy(self, instance):
        instance.delete()


class StudentTianKongAnswerView(mixins.CreateModelMixin,mixins.ListModelMixin,mixins.UpdateModelMixin,mixins.RetrieveModelMixin,viewsets.GenericViewSet):
    '''
    list:
        学生填空答案列表
    retrieve:
        学生填空答案详情
    create:
        学生创建填空答案
    update:
        学生更改填空答案
    partial_update:
        学生部分更改填空答案
    '''
    pagination_class = DefaultPagination
    permission_classes = (IsAuthenticated,)
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    filter_class = StudentTianKongAnswerFilter
    ordering_fields = ('blank__number',)
    def get_serializer_class(self):
        if self.action in ['list','retrieve']:
            return StudentTianKongAnswerListSerializer
        elif self.action=='create':
            return StudentTianKongAnswerCreateSerializer
        else:
            return StudentTianKongAnswerUpdateSerializer
    def get_queryset(self):
        user=self.request.user
        if user.is_student:
            return StudentTianKongAnswer.objects.filter(student=user.student)
        elif user.is_teacher:
            return StudentTianKongAnswer.objects.all()
        else:
            return None


class JianDaAnswerView(mixins.ListModelMixin,mixins.RetrieveModelMixin,mixins.CreateModelMixin,mixins.UpdateModelMixin,viewsets.GenericViewSet):
    '''
    list:
        简答题参考答案列表
    retrieve:
        简答题参考答案详情
    create:
        创建简答题参考答案
    update:
        更改简答题参考答案
    partial_update:
        部分更改简答题参考答案
    '''
    pagination_class = DefaultPagination
    permission_classes = (IsAuthenticated,)
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    filter_class = JianDaAnswerViewFilter
    # ordering_fields = ('blank__number',)
    def get_queryset(self):
        user=self.request.user
        if user.is_student:
            return JianDaAnswer.objects.filter(question__homework__limit_time__lt=datetime.now())
        elif user.is_teacher:
            return JianDaAnswer.objects.filter(question__homework__lesson_period__schedule_lesson__teacher=user.teacher)
        else:
            return None
    def get_serializer_class(self):
        if self.action=='list' or self.action=='retrieve':
            return JianDaAnswerListSerializer
        elif self.action=='create':
            return JianDaAnswerCreateSerializer
        else:
            return JianDaAnswerUpdateSerializer

class StudentJianDaAnswerView(mixins.ListModelMixin,mixins.RetrieveModelMixin,mixins.CreateModelMixin,mixins.UpdateModelMixin,viewsets.GenericViewSet):
    '''
    list:
        学生简答题答案列表
    retrieve:
        学生简答题答案详情
    create:
        学生创建简答题答案
    update:
        学生更改简答特答案
    partial_update:
        学生部分更改简答题答案
    '''
    pagination_class = DefaultPagination
    permission_classes = (IsAuthenticated,)
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    filter_class = StudentJianDaAnswerFilter
    ordering_fields = ('student','question',)
    def get_serializer_class(self):
        if self.action=='list' or self.action=='retrieve':
            return StudentJianDaAnswerListSerializer
        elif self.action=='action':
            return StudentJianDaAnswerCreateSerializer
        else:
            return StudentJianDaAnswerUpdateSerializer
    def get_queryset(self):
        user=self.request.user
        if user.is_student:
            return StudentJianDaAnswer.objects.filter(student=user.student)
        elif user.is_teacher:
            return StudentJianDaAnswer.objects.all()
        else:
            return None

class OtherAnswerImageView(mixins.CreateModelMixin,mixins.UpdateModelMixin,mixins.DestroyModelMixin,viewsets.GenericViewSet):
    '''
    create:
        创建其他答案图片
    update:
        更改其他答案图片序号
    partial_update:
        部分更改其他答案序号
    '''
    permission_classes = (IsAuthenticated,)
    def get_serializer_class(self):
        if self.action=='create':
            return OtherAnswerImageCreateSerializer
        else:
            return OtherAnswerImageUpdateSerializer
    def get_queryset(self):
        return OtherAnswerImage.objects.all()
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        user=self.request.user
        if not user.is_teacher:
            return response.Response(status=status.HTTP_403_FORBIDDEN)
        teacher=user.teacher
        other_answer=instance.other_answer
        if other_answer.question.homework.lesson_period.schedule_lesson.teacher!=teacher:
            return response.Response(status=status.HTTP_403_FORBIDDEN)
        self.perform_destroy(instance)
        other_answer.image_count-=1
        other_answer.save()
        return response.Response(status=status.HTTP_204_NO_CONTENT)
    def perform_destroy(self, instance):
        instance.delete()



class OtherAnswerView(mixins.ListModelMixin,mixins.CreateModelMixin,mixins.UpdateModelMixin,mixins.RetrieveModelMixin,viewsets.GenericViewSet):
    '''
    list:
        查看其他答案列表
    retrieve:
        查看其他答案详情
    update:
        更改其他答案
    partial_update:
        部分更改其他答案
    '''
    pagination_class = DefaultPagination
    permission_classes = (IsAuthenticated,)
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    filter_class = OtherAnswerFilter
    ordering_fields = ('student', 'question',)
    def get_queryset(self):
        user=self.request.user
        if user.is_teacher:
            return OtherAnswer.objects.all()
        elif user.is_student:
            return OtherAnswer.objects.filter(question__homework__limit_time__lt=datetime.now())
    def get_serializer_class(self):
        if self.action=='list' or self.action=='retrieve':
            return OtherAnswerListSerializer
        elif self.action=='create':
            return OtherAnswerCreateSerializer
        else:
            return OtherAnswerUpdateSerializer

class StudentOtherAnswerImageView(mixins.CreateModelMixin,mixins.UpdateModelMixin,mixins.DestroyModelMixin,viewsets.GenericViewSet):
    '''
    create:
        学生创建其他答案图片
    update:
        学生更改其他答案图片
    partial:
        学生部分更改其他答案图片
    destroy:
        学生删除其他答案图片
    '''
    permission_classes = (IsAuthenticated,)
    def get_serializer_class(self):
        if self.action=='create':
            return StudentOtherAnswerImageCreateSerializer
        else:
            return StudentOtherAnswerImageUpdateSerializer
    def get_queryset(self):
        user=self.request.user
        if user.is_student:
            return StudentOtherAnswerImage.objects.filter(student_other_answer__student=user.student)
        return None
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        user = self.request.user
        if not user.is_student:
            return response.Response(status=status.HTTP_403_FORBIDDEN)
        student = user.student
        student_other_answer = instance.student_other_answer
        if student_other_answer.student!=student:
            return response.Response(status=status.HTTP_403_FORBIDDEN)
        self.perform_destroy(instance)
        student_other_answer.image_count -= 1
        student_other_answer.save()
        return response.Response(status=status.HTTP_204_NO_CONTENT)
    def perform_destroy(self, instance):
        instance.delete()

class StudentOtherAnswerView(mixins.ListModelMixin,mixins.RetrieveModelMixin,mixins.CreateModelMixin,mixins.UpdateModelMixin,viewsets.GenericViewSet):
    '''
    list:
        学生其他答案列表
    retrieve:
        学生其他答案详情
    create:
        学生创建其他答案
    update:
        学生更改其他答案
    partial_update:
        学生部分更改其他答案
    '''
    pagination_class = DefaultPagination
    permission_classes = (IsAuthenticated,)
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    filter_class = StudentOtherAnswerFilter
    ordering_fields = ('student', 'question',)
    def get_serializer_class(self):
        if self.action=='list' or self.action=='retrieve':
            return StudentOtherAnswerListSerializer
        elif self.action=='create':
            return StudentOtherAnswerCreateSerializer
        else:
            return StudentOtherAnswerUpdateSerializer
    def get_queryset(self):
        user=self.request.user
        if user.is_student:
            return StudentOtherAnswer.objects.filter(student=user.student)
        elif user.is_teacher:
            return StudentOtherAnswer.objects.all()
        else:
            return None

class DaiMaFileView(mixins.ListModelMixin,mixins.RetrieveModelMixin,mixins.CreateModelMixin,mixins.UpdateModelMixin,mixins.DestroyModelMixin,viewsets.GenericViewSet):
    '''
    list:
        代码文件列表
    retrieve:
        代码文件详情
    create:
        创建代码文件
    update:
        更改代码文件
    partial_update:
        部分更改代码文件
    destroy:
        删除代码文件
    '''
    pagination_class = DefaultPagination
    permission_classes = (IsAuthenticated,)
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    filter_class = DaiMaFileFilter
    ordering_fields = ('question',)
    def get_serializer_class(self):
        if self.action=='list' or self.action=='retrieve':
            return DaiMaFileListSerializer
        elif self.action=='create':
            return DaiMaFileCreateSerializer
        else:
            return DaiMaFileUpdateSerializer
    def get_queryset(self):
        return DaiMaFile.objects.all()
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        user=self.request.user
        if not user.is_teacher:
            return response.Response(status=status.HTTP_403_FORBIDDEN)
        teacher=user.teacher
        if teacher!=instance.question.homework.lesson_period.schedule_lesson.teacher:
            return response.Response(status=status.HTTP_403_FORBIDDEN)
        self.perform_destroy(instance)
        return response.Response(status=status.HTTP_204_NO_CONTENT)
    def perform_destroy(self, instance):
        instance.delete()

class DaiMaAnswerView(mixins.ListModelMixin,mixins.RetrieveModelMixin,mixins.CreateModelMixin,mixins.UpdateModelMixin,viewsets.GenericViewSet):
    '''
    list:
        代码答案列表
    retrieve:
        代码答案详情
    create:
        创建代码答案
    update:
        更改代码答案
    partial_update:
        部分更改代码答案
    '''
    pagination_class = DefaultPagination
    permission_classes = (IsAuthenticated,)
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    filter_class = DaiMaAnswerFilter
    ordering_fields = ('daima_type',)
    def get_serializer_class(self):
        if self.action=='list' or self.action=='retrieve':
            return DaiMaAnswerListSerializer
        elif self.action=='create':
            return DaiMaAnswerCreateSerializer
        else:
            return DaiMaAnswerUpdateSerializer
    def get_queryset(self):
        user=self.request.user
        if user.is_teacher:
            return DaiMaAnswer.objects.all()
        elif user.is_student:
            return DaiMaAnswer.objects.filter(daima_file__question__homework__limit_time__lt=datetime.now())


class StudentDaiMaAnswerView(mixins.ListModelMixin,mixins.RetrieveModelMixin,mixins.CreateModelMixin,mixins.UpdateModelMixin,viewsets.GenericViewSet):
    '''
    list:
        学生代码答案列表
    retrieve:
        学生代码答案详情
    create:
        学生创建代码答案
    update:
        学生更改代码答案
    partial_update:
        学生部分更改代码答案
    '''
    pagination_class = DefaultPagination
    permission_classes = (IsAuthenticated,)
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    filter_class = StudentDaiMaAnswerFilter
    ordering_fields = ('daima_type','student')
    def get_serializer_class(self):
        if self.action=='list' or self.action=='retrieve':
            return StudentDaiMaAnswerListSerializer
        elif self.action=='create':
            return StudentDaiMaAnswerCreateSerializer
        else:
            return StudentDaiMaAnswerUpdateSerializer
    def get_queryset(self):
        user=self.request.user
        if user.is_student:
            return StudentDaiMaAnswer.objects.filter(student=user.student)
        elif user.is_teacher:
            return StudentDaiMaAnswer.objects.all()
        else:
            return None

class QuestionScoreView(mixins.ListModelMixin,mixins.RetrieveModelMixin,mixins.CreateModelMixin,mixins.UpdateModelMixin,viewsets.GenericViewSet):
    '''
    list:
        单题得分列表
    create:
        创建单题得分
    update:
        更改单题得分
    partial_update:
        部分更改单题得分
    retrieve:
        单题得分详情
    '''
    pagination_class = DefaultPagination
    permission_classes = (IsAuthenticated,)
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    filter_class = QuestionScoreFilter
    ordering_fields = ('student','question','score')
    def get_serializer_class(self):
        if self.action=='list' or self.action=='retrieve':
            return QuestionScoreListSerializer
        elif self.action=='create':
            return QuestionScoreCreateSerializer
        else:
            return QuestionScoreUpdateSerializer
    def get_queryset(self):
        user=self.request.user
        if user.is_student:
            return QuestionScore.objects.filter(student=user.student)
        elif user.is_teacher:
            return QuestionScore.objects.all()
        else:
            return None

class AutoCorrectNoSubmitHomeworkView(mixins.CreateModelMixin,viewsets.GenericViewSet):
    '''
    create:
        自动批改未提交、未答的作业
    '''
    permission_classes = (IsAuthenticated,)
    def get_serializer_class(self):
        return AutoCorrectNoSubmitHomeworkSerialier
    def create(self, request, *args, **kwargs):
        data=request.data
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        auto_correct_no_submit_homework.delay(homework_id=data.dict['homework_id'])
        headers = self.get_success_headers(serializer.data)
        return response.Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    def perform_create(self, serializer):
        serializer.save()


