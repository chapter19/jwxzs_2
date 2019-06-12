from django.db import models
from datetime import datetime

from users.models import UserProfile
from lessons.models import ScheduleLesson

# Create your models here.

class TheCheck(models.Model):
    promoter=models.ForeignKey(UserProfile,verbose_name='发起人',related_name='my_initiate_check')
    schedule_lesson=models.ForeignKey(ScheduleLesson,verbose_name='课堂班级',related_name='the_check')
    check_status=models.CharField(choices=(('waiting','待开启'),('checking','正在进行'),('timeout','已过期')),max_length=20,verbose_name='点到状态',default='waiting')
    start_time=models.DateTimeField(default=datetime.now,verbose_name='开始时间')
    time_limit=models.IntegerField(default=3,verbose_name='几分钟后结束')
    password=models.IntegerField(verbose_name='密码',blank=True,null=True)
    class Meta:
        verbose_name='点到'
        verbose_name_plural=verbose_name
    def __str__(self):
        return self.schedule_lesson.class_name


class CheckedStudent(models.Model):
    the_check=models.ForeignKey(TheCheck,verbose_name='点到',related_name='checked_student',on_delete=models.CASCADE)
    check_time=models.DateTimeField(verbose_name='确认时间',blank=True,null=True)
    student=models.ForeignKey(UserProfile,verbose_name='学生',related_name='checked_student')
    class Meta:
        verbose_name='已点到学生'
        verbose_name_plural=verbose_name
    def __str__(self):
        return self.student.name



























