#-*- coding:utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from datetime import datetime
from users.models import Student
from lessons.models import Lesson,ScheduleLesson


class Score(models.Model):
    # student_id=models.CharField(max_length=12,verbose_name=u'学号',default='')
    student=models.ForeignKey(Student,verbose_name=u'学生',on_delete=models.CASCADE,related_name='score')
    schedule_lesson = models.ForeignKey(ScheduleLesson, verbose_name=u'课表课程', default='',on_delete=models.CASCADE,related_name='score')
    score=models.FloatField(verbose_name=u'成绩',default=0.0,null=True,blank=True)
    standard_score=models.FloatField(verbose_name=u'标准分',default=-20.0,null=True,blank=True)
    rescore=models.FloatField(verbose_name=u'补考成绩',null=True,blank=True)
    if_major=models.BooleanField(default=False,verbose_name=u'是否为专业课')
    add_time = models.DateTimeField(default=datetime.now, verbose_name=u'添加时间')
    class Meta:
        verbose_name=u'成绩'
        verbose_name_plural=verbose_name
        unique_together = ('schedule_lesson','student')
    def __str__(self):
        return self.schedule_lesson.lesson.name


class NewScore(models.Model):
    student = models.ForeignKey(Student, verbose_name=u'学生',on_delete=models.CASCADE)
    schedule_lesson = models.ForeignKey(ScheduleLesson, verbose_name=u'课表课程', default='',on_delete=models.CASCADE)
    algorithm=models.CharField(max_length=35,verbose_name=u'算法',null=True,blank=True)
    daily_score=models.FloatField(verbose_name=u'平时成绩',null=True,blank=True)
    practical_score=models.FloatField(verbose_name=u'实践成绩',null=True,blank=True)
    theoretical_score=models.FloatField(default=0.0,verbose_name=u'理论成绩',null=True,blank=True)
    score=models.FloatField(default=0.0,verbose_name=u'总评成绩')
    if_major = models.BooleanField(default=False, verbose_name=u'是否为专业课')
    add_time = models.DateTimeField(default=datetime.now, verbose_name=u'添加时间')
    class Meta:
        verbose_name=u'最新成绩'
        verbose_name_plural=verbose_name
        unique_together = ('schedule_lesson', 'student')
    def __str__(self):
        return self.schedule_lesson.lesson.name


class TotalCredit(models.Model):
    student=models.OneToOneField(Student,verbose_name=u'学生',on_delete=models.CASCADE)
    credit=models.IntegerField(verbose_name=u'已修学分',default=0)
    standard_score=models.FloatField(verbose_name='加权平均标准分')
    add_time = models.DateTimeField(default=datetime.now, verbose_name=u'添加时间')
    class Meta:
        verbose_name=u'总学分'
        verbose_name_plural=verbose_name
    def __str__(self):
        return self.student.name














