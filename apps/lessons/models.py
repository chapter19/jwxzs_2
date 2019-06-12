#-*- coding:utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from datetime import datetime

from users.models import Teacher,Major,Colloge


class Lesson(models.Model):
    id = models.CharField(max_length=15, verbose_name=u'课程号', default='', primary_key=True)
    name=models.CharField(max_length=50,verbose_name=u'课程名称',default='')
    credit=models.IntegerField(verbose_name=u'学分',default=2)
    if_public_elective=models.BooleanField(verbose_name=u'是否为公选',default=False)
    before_learning_text=models.CharField(verbose_name='先修课程说明',blank=True,null=True,max_length=100,help_text='先修课程说明')
    profile=models.TextField(verbose_name='课程简介',blank=True,null=True,help_text='课程简介')
    admin_department = models.ForeignKey(Colloge, verbose_name='管理部门',blank=True,null=True)
    open_semester=models.CharField(max_length=30,verbose_name='开课学期说明',blank=True,null=True)
    add_time = models.DateTimeField(default=datetime.now, verbose_name=u'添加时间')
    class Meta:
        verbose_name=u'课程'
        verbose_name_plural=verbose_name
    def __str__(self):
        return self.name



class MajorLesson(models.Model):
    major=models.ForeignKey(Major,verbose_name=u'专业',on_delete=models.CASCADE)
    lesson=models.ForeignKey(Lesson,verbose_name=u'课程',on_delete=models.CASCADE)
    lesson_type = models.IntegerField(choices=((1,u'公共必修'),(2,u'学科基础'),(3,u'专业主干'),(4,u'专业任选'),(5,u'专业限选')),verbose_name=u'课程性质')
    if_degree=models.BooleanField(verbose_name=u'是否为学位课程',default=False)
    major_directions=models.CharField(max_length=30,verbose_name=u'主修方向',null=True,blank=True)
    add_time = models.DateTimeField(default=datetime.now, verbose_name=u'添加时间')
    open_semester=models.IntegerField(default=1,verbose_name='开课学期')
    limit_lesson_minimum_credit = models.IntegerField(verbose_name='限选课最低毕业学分', null=True, blank=True,help_text='限选课最低毕业学分')
    class Meta:
        verbose_name=u'专业培养方案课程'
        verbose_name_plural=verbose_name
    def __str__(self):
        return str(self.major)+str(self.lesson)


class ScheduleLesson(models.Model):
    # id=models.CharField(max_length=20,verbose_name='id',primary_key=True,db_column='FId')
    class_id=models.CharField(max_length=20,verbose_name=u'课程班级号',)
    class_name=models.CharField(max_length=30,verbose_name=u'课程班级名',default='')
    semester=models.CharField(max_length=20,verbose_name=u'学期')
    lesson=models.ForeignKey(Lesson,verbose_name=u'课程',on_delete=models.CASCADE,related_name='schedule_lesson')
    teacher=models.ForeignKey(Teacher,verbose_name=u'教师',null=True,blank=True,on_delete=models.CASCADE,related_name='schedule_lesson')
    add_time = models.DateTimeField(default=datetime.now, verbose_name=u'添加时间')
    class Meta:
        verbose_name=u'课程表课程'
        verbose_name_plural=verbose_name
        unique_together = ('class_id', 'semester','lesson')
    def __str__(self):
        return self.lesson.name


class Schedule(models.Model):
    class_room = models.CharField(max_length=10, verbose_name=u'教室')
    counter = models.IntegerField(verbose_name=u'课时编号')
    schedule_lesson=models.ForeignKey(ScheduleLesson,verbose_name=u'课程信息',on_delete=models.CASCADE)
    add_time = models.DateTimeField(default=datetime.now, verbose_name=u'添加时间')
    class Meta:
        verbose_name=u'课程表'
        verbose_name_plural=verbose_name
        unique_together=('counter','schedule_lesson')
    def __str__(self):
        return self.schedule_lesson.lesson.name


class ErrorSchedule(models.Model):
    teacher_id=models.CharField(max_length=20,default='')
    semester=models.CharField(max_length=30,default='')
    add_time = models.DateTimeField(default=datetime.now, verbose_name=u'添加时间')
    def __str__(self):
        return str(self.teacher_id)+str(self.semester)














