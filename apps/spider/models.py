from django.db import models
from datetime import datetime
import uuid

from users.models import UserProfile

# Create your models here.

class SpiderLog(models.Model):
    verbose_id=models.UUIDField(default=uuid.uuid4(),verbose_name='第二个的id')
    url=models.CharField(max_length=200,verbose_name='URL',blank=True,null=True)
    task_id=models.CharField(max_length=70,verbose_name='任务id',blank=True,null=True)
    desc=models.CharField(max_length=200,verbose_name='描述',default='')
    spider_class_and_method=models.CharField(max_length=200,verbose_name='爬虫类和方法',default='')
    start_time=models.DateTimeField(default=datetime.now,verbose_name='开始时间')
    type=models.CharField(choices=(('Major','专业'),('Colloge','学院'),('Class','班级'),('Student','学生'),('Department','部门'),('Teacher','教师'),('Schedule','课表'),('Score','成绩'),('NewScore','最新成绩')),max_length=16,verbose_name='类型',blank=True,null=True)
    stop_time=models.DateTimeField(verbose_name='结束时间',blank=True,null=True)
    status=models.CharField(max_length=8,choices=(('getting','正在爬取'),('end','爬取结束'),('error','爬取异常'),('retried','已重试'),('stopped','已终止')),default='getting',verbose_name='状态')
    user=models.ForeignKey(UserProfile,verbose_name='操作人',blank=True,null=True)
    class Meta:
        verbose_name='爬取日志'
        verbose_name_plural=verbose_name
    def __str__(self):
        return self.desc


class SpiderLogDetail(models.Model):
    spider_log=models.ForeignKey(SpiderLog,verbose_name='爬取日志',blank=True,null=True)
    desc=models.CharField(max_length=200,verbose_name='描述',default='')
    model=models.CharField(choices=(('Student','学生'),('Colloge','学院'),('Class','班级'),('Department','教工部门'),('Teacher','教师'),('ScheduleLesson','课程表课程'),('Schedule','课程表'),('Score','成绩(名单)'),('Redio','教务通知'),('NewScore','最新成绩'),('Major','专业'),('MajorLesson','专业培养方案课程')),max_length=30,verbose_name='数据模型',default='Student')
    status=models.CharField(choices=(('success','插入成功'),('fail','失败，已存在')),max_length=8,verbose_name='爬取状态',default='success')
    create_time=models.DateTimeField(default=datetime.now,verbose_name='创建时间')
    class Meta:
        verbose_name='爬虫数据表日志'
        verbose_name_plural=verbose_name
    def __str__(self):
        return self.desc

class Timer(models.Model):
    hours=models.IntegerField(verbose_name='几小时更新',default=2)
    type=models.CharField(choices=(('Redio','教务通知'),('TeacherPhoto','教师照片'),('StudentPhoto','学生照片')),max_length=18,verbose_name='定时更新器类型',default='Redio')
    class Meta:
        verbose_name='自动更新定时器'
        verbose_name_plural=verbose_name
    def __str__(self):
        return self.type

