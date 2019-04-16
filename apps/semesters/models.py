from django.db import models
from datetime import datetime

class Semester(models.Model):
    post_code=models.CharField(max_length=30,verbose_name='表单码',blank=True,null=True)
    verbose_name=models.CharField(max_length=50,verbose_name='显示名称',default='',unique=True)
    add_time=models.DateTimeField(default=datetime.now,verbose_name='添加时间')
    if_spider_grade=models.BooleanField(default=False,verbose_name='是否爬取该年级')
    if_spider_semester=models.BooleanField(default=False,verbose_name='是否爬取该学期')
    class Meta:
        verbose_name='学期'
        verbose_name_plural=verbose_name
    def __str__(self):
        return self.verbose_name


class CurrentSemester(models.Model):
    # name=models.CharField()
    current_semester=models.ForeignKey(Semester,verbose_name='当前学期',related_name='current_semester')
    add_time = models.DateTimeField(default=datetime.now, verbose_name='添加时间')
    update_time=models.DateTimeField(verbose_name='修改时间',default=datetime.now)
    class Meta:
        verbose_name='当前学期'
        verbose_name_plural=verbose_name
    def __str__(self):
        return self.current_semester.verbose_name



