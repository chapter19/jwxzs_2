#-*- coding:utf-8 -*-

import django_filters
from .models import KnowledgeLabel,Unit,LessonPeriod,Homework,Question,QuestionImage,Choice,\
    StudentChoiceAnswer,ChoiceTrueAnswer,PanDuanTrueAnswer,StudentPanDuanAnswer,TianKongBlank,\
    TianKongTrueAnswer,TianKongOtherAnswer,StudentTianKongAnswer,JianDaAnswer,StudentJianDaAnswer,\
    OtherAnswer,StudentOtherAnswer,DaiMaFile,DaiMaAnswer,StudentDaiMaAnswer,QuestionScore,HomeworkScore


class KnowledgeLabelFilter(django_filters.rest_framework.FilterSet):
    semester=django_filters.CharFilter(field_name='semester__post_code',lookup_expr='exact',label='学期表单码',help_text='学期表单码')
    class Meta:
        model=KnowledgeLabel
        fields=['lesson','teacher','semester']


class UnitFilter(django_filters.rest_framework.FilterSet):
    class Meta:
        model=Unit
        fields=['semester','lesson','teacher','unit_type','create_user']


class LessonPeriodFilter(django_filters.rest_framework.FilterSet):
    class Meta:
        model=LessonPeriod
        fields=['schedule_lesson','unit']


class HomeworkFilter(django_filters.rest_framework.FilterSet):
    schedule_lesson=django_filters.NumberFilter(field_name='lesson_period__schedule_lesson',lookup_expr='exact',label='课程表课程id',help_text='课程表课程id')
    class Meta:
        model=Homework
        fields=['lesson_period','schedule_lesson']


class QuestionImageFilter(django_filters.rest_framework.FilterSet):
    class Meta:
        model=QuestionImage
        fields=['question']


class QuestionFilter(django_filters.rest_framework.FilterSet):
    schedule_lesson = django_filters.NumberFilter(field_name='homework__lesson_period__schedule_lesson', lookup_expr='exact',label='课程表课程id', help_text='课程表课程id')
    class Meta:
        model=Question
        fields=['schedule_lesson','homework']

class ChoiceFilter(django_filters.rest_framework.FilterSet):
    class Meta:
        model=Choice
        fields=['question']


class StudentChoiceAnswerFilter(django_filters.rest_framework.FilterSet):
    class Meta:
        model=StudentChoiceAnswer
        fields=['student','question','choice']


class ChoiceTrueAnswerFilter(django_filters.rest_framework.FilterSet):
    class Meta:
        model=ChoiceTrueAnswer
        fields=['question']

class PanDuanTrueAnswerFilter(django_filters.rest_framework.FilterSet):
    class Meta:
        model=PanDuanTrueAnswer
        fields=['question']

class StudentPanDuanAnswerFilter(django_filters.rest_framework.FilterSet):
    class Meta:
        model=StudentPanDuanAnswer
        fields=['question','student','answer']

class TianKongBlankFilter(django_filters.rest_framework.FilterSet):
    class Meta:
        model=TianKongBlank
        fields=['question','if_other_answer']

class TianKongTrueAnswerFilter(django_filters.rest_framework.FilterSet):
    class Meta:
        model=TianKongTrueAnswer
        fields=['blank','blank__question']

class TianKongOtherAnswerFilter(django_filters.rest_framework.FilterSet):
    class Meta:
        model=TianKongOtherAnswer
        fields=['blank','blank__question']

class StudentTianKongAnswerFilter(django_filters.rest_framework.FilterSet):
    class Meta:
        model=StudentTianKongAnswer
        fields=['student','blank','answer']

class JianDaAnswerViewFilter(django_filters.rest_framework.FilterSet):
    class Meta:
        model=JianDaAnswer
        fields=['answer','question']

class StudentJianDaAnswerFilter(django_filters.rest_framework.FilterSet):
    class Meta:
        model=StudentJianDaAnswer
        fields=['student','if_auto_submit','question']

class OtherAnswerFilter(django_filters.rest_framework.FilterSet):
    class Meta:
        model=OtherAnswer
        fields=['question']

class StudentOtherAnswerFilter(django_filters.rest_framework.FilterSet):
    class Meta:
        model=StudentOtherAnswer
        fields=['question','student']

class DaiMaFileFilter(django_filters.rest_framework.FilterSet):
    class Meta:
        model=DaiMaFile
        fields=['question','daima_type','name']

class DaiMaAnswerFilter(django_filters.rest_framework.FilterSet):
    class Meta:
        model=DaiMaAnswer
        fields=['daima_file','daima_type','daima_file__question']

class StudentDaiMaAnswerFilter(django_filters.rest_framework.FilterSet):
    class Meta:
        model=StudentDaiMaAnswer
        fields=['daima_file','student','daima_file__question','daima_type']

class QuestionScoreFilter(django_filters.rest_framework.FilterSet):
    score_max=django_filters.NumberFilter(field_name='score',lookup_expr='lte',label='得分小于等于',help_text='得分小于等于')
    score_min=django_filters.NumberFilter(field_name='score',lookup_expr='gte',label='得分大于等于',help_text='得分大于等于')
    class Meta:
        model=QuestionScore
        fields=['student','question','score_max','score_min']

class HomeworkScoreFilter(django_filters.rest_framework.FilterSet):
    total_score_max=django_filters.NumberFilter(field_name='total_score',lookup_expr='lte',label='成绩小于等于',help_text='成绩小于等于')
    total_score_min=django_filters.NumberFilter(field_name='total_score',lookup_expr='gte',label='成绩大于等于',help_text='成绩大于等于')
    class Meta:
        model=HomeworkScore
        fields=['homework','student','total_score_max','total_score_min','homework__lesson_period__schedule_lesson']