#-*- coding:utf-8 -*-
from __future__ import unicode_literals
from datetime import datetime
from django.db import models
from django.contrib.auth.models import AbstractUser


class Major(models.Model):
    id=models.CharField(max_length=20,verbose_name='id',default='',primary_key=True)
    major_id=models.CharField(max_length=10,verbose_name=u'专业号',default='')
    post_code=models.CharField(max_length=20,verbose_name=u'表单码',default='')
    grade = models.IntegerField(verbose_name=u'年级', null=True, blank=True)
    name=models.CharField(max_length=100,verbose_name=u'专业名称',default='')
    training_objectives = models.TextField(verbose_name=u'培养目标', null=True, blank=True, default=None)
    # basic_knowledge = models.TextField(verbose_name=u'基础知识', null=True, blank=True, default=None)
    # major_knowledge = models.TextField(verbose_name=u'专业知识', null=True, blank=True, default=None)
    direction_introduction=models.TextField(verbose_name=u'方向介绍',null=True,blank=True,default=None)
    subject=models.CharField(max_length=100,verbose_name=u'隶属科类',null=True,blank=True,default=None)
    main_subject=models.CharField(max_length=100,verbose_name=u'主干学科',null=True,blank=True,default=None)
    similar_major=models.CharField(max_length=100,verbose_name=u'类近专业',null=True,blank=True,default=None)
    education_background=models.CharField(max_length=50,verbose_name=u'学历',null=True,blank=True,default=u'本科')
    degree=models.CharField(max_length=50,verbose_name=u'授予学位',null=True,blank=True)
    length_of_schooling=models.IntegerField(verbose_name=u'标准学制(年)',default=4)
    minimum_graduation_credit=models.IntegerField(verbose_name=u'最低毕业学分',default=160)
    add_time = models.DateTimeField(default=datetime.now, verbose_name=u'添加时间')
    if_multiple_directions=models.BooleanField(default=False,verbose_name=u'是否有多个方向')

    class Meta:
        verbose_name=u'专业'
        verbose_name_plural=verbose_name
        unique_together=('major_id','grade')
    def __str__(self):
        return str(self.grade)+'级'+str(self.name)


class Colloge(models.Model):
    id=models.CharField(max_length=15,verbose_name=u'学院号',default='',primary_key=True)
    post_code=models.CharField(max_length=30,verbose_name=u'表单码',default='')
    name=models.CharField(max_length=30,verbose_name=u'学院名称',default='')
    add_time = models.DateTimeField(default=datetime.now, verbose_name=u'添加时间')
    class Meta:
        verbose_name=u'学院'
        verbose_name_plural=verbose_name

    def get_class_nums(self):
        '''学院班级数'''
        return self.class_set.all().count()
    get_class_nums.short_description='班级数'

    def __str__(self):
        return self.name


class Class(models.Model):
    id=models.CharField(max_length=20,verbose_name=u'班级号',primary_key=True)
    post_code = models.CharField(max_length=30, verbose_name=u'表单码', default='')
    name=models.CharField(max_length=70,verbose_name=u'班级名')
    grade=models.IntegerField(verbose_name=u'年级',null=True,blank=True)
    major=models.ForeignKey(Major,verbose_name=u'专业',null=True,blank=True,on_delete=models.CASCADE)
    colloge=models.ForeignKey(Colloge,verbose_name=u'学院',on_delete=models.CASCADE)
    add_time = models.DateTimeField(default=datetime.now, verbose_name=u'添加时间')
    class Meta:
        verbose_name=u'班级'
        verbose_name_plural=verbose_name
    def get_student_nums(self):
        return self.student_set.all().count()
    get_student_nums.short_description='学生数'
    def __str__(self):
        return self.name


class UserProfile(AbstractUser):
    name=models.CharField(max_length=50,verbose_name=u'姓名',default='')
    gender = models.CharField(choices=(('male', u'男'), ('female', u'女')), max_length=6, default='female',verbose_name='性别',help_text='性别')
    # type=models.CharField(choices=(('student','学生'),('teacher','教师'),('admin','')))
    is_student=models.BooleanField(default=False,verbose_name=u'是否为学生')
    is_teacher=models.BooleanField(default=False,verbose_name=u'是否为教师')
    class Meta:
        verbose_name=u'用户信息'
        verbose_name_plural=verbose_name
    def __str__(self):
        return self.username


class Student(models.Model):
    id=models.CharField(max_length=12,verbose_name=u'学号',primary_key=True,help_text='学号')
    name=models.CharField(max_length=50,verbose_name=u'姓名',default='',help_text='姓名')
    cla=models.ForeignKey(Class,verbose_name=u'班级',null=True,blank=True,on_delete=models.CASCADE)
    gender=models.CharField(choices=(('male',u'男'),('female',u'女')),max_length=6,default='female',verbose_name=u'性别',help_text='性别')
    user=models.OneToOneField(UserProfile,verbose_name='用户',null=True,blank=True)
    add_time = models.DateTimeField(default=datetime.now, verbose_name=u'添加时间')
    class Meta:
        verbose_name=u'学生'
        verbose_name_plural=verbose_name
    def __str__(self):
        return self.name



class StudentDetail(models.Model):
    base_data=models.OneToOneField(Student,verbose_name=u'基本信息',null=True,blank=True)
    # cla = models.ForeignKey(Class, verbose_name=u'班级')
    candidate_id=models.CharField(max_length=25,verbose_name=u'考生号',null=True,blank=True)
    nationality=models.CharField(max_length=30,verbose_name=u'民族',default='汉族')
    birthday=models.DateField(verbose_name=u'生日',null=True,blank=True)
    id_card=models.CharField(max_length=18,verbose_name=u'身份证号',null=True,blank=True)
    political_status=models.CharField(max_length=30,verbose_name=u'政治面貌',null=True,blank=True)
    birthplace=models.CharField(max_length=30,verbose_name=u'籍贯',null=True,blank=True)
    email=models.EmailField(null=True,blank=True,verbose_name=u'电子邮箱')
    mobile=models.CharField(max_length=11,null=True,blank=True,verbose_name=u'通讯号码')
    # user_profile=models.OneToOneField(UserProfile,on_delete=models.CASCADE)
    add_time = models.DateTimeField(default=datetime.now, verbose_name=u'添加时间')
    class Meta:
        verbose_name=u'学生详细信息'
        verbose_name_plural=verbose_name
    def __str__(self):
        return self.base_data.name


class Department(models.Model):
    id=models.CharField(max_length=20,verbose_name=u'单位id',primary_key=True)
    name=models.CharField(max_length=35,verbose_name=u'单位名称')
    post_code = models.CharField(max_length=30, verbose_name=u'表单码', default='')
    add_time = models.DateTimeField(default=datetime.now, verbose_name=u'添加时间')
    class Meta:
        verbose_name=u'教工单位'
        verbose_name_plural=verbose_name

    def get_teacher_nums(self):
        return self.teacher_set.all().count()
    get_teacher_nums.short_description='教师数'

    def __str__(self):
        return self.name


class Teacher(models.Model):
    id=models.CharField(max_length=10,verbose_name=u'教号',primary_key=True)
    name=models.CharField(max_length=50,verbose_name=u'姓名')
    gender = models.CharField(choices=(('male', u'男'), ('female', u'女')), verbose_name=u'性别' ,max_length=6, default='female')
    department=models.ForeignKey(Department,verbose_name=u'部门',null=True,blank=True,on_delete=models.CASCADE)
    user = models.OneToOneField(UserProfile, verbose_name='用户', null=True, blank=True)
    add_time = models.DateTimeField(default=datetime.now, verbose_name=u'添加时间')
    class Meta:
        verbose_name=u'教师'
        verbose_name_plural=verbose_name
    def __str__(self):
        return self.name

















