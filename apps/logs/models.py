from django.db import models

from users.models import UserProfile

from datetime import datetime

# Create your models here.

class Log(models.Model):
    user=models.ForeignKey(UserProfile,verbose_name='用户',related_name='my_log')
    ip=models.GenericIPAddressField(verbose_name='ip',default='')
    action_time=models.DateTimeField(default=datetime.now,verbose_name='操作时间')
    action_type=models.CharField(max_length=6,choices=(('match','查询'),('delete','删除'),('create','增加'),('update','更改'),('other','其他')),verbose_name='操作方式',default='')
    message=models.CharField(max_length=200,verbose_name='操作内容',default='')
    address=models.CharField(verbose_name='地址',max_length=100,blank=True,null=True,default='')
    class Meta:
        verbose_name='日志'
        verbose_name_plural=verbose_name
    def __str__(self):
        return self.message


class Ip(models.Model):
    ip = models.GenericIPAddressField(verbose_name='ip',default='',primary_key=True)
    address = models.CharField(verbose_name='地址', max_length=100,default='')
    adcode=models.CharField(verbose_name='行政编码',max_length=10,default='')
    rectangle=models.CharField(verbose_name='经纬度',max_length=100,default='')
    class Meta:
        verbose_name='IP和地址'
        verbose_name_plural=verbose_name
    def __str__(self):
        return self.address


#搜索记录
# class SearchLog(models.Model):
#     search_type=models.CharField(choices=(()),max_length=10,verbose_name='搜索类型')
#     words=models.CharField(max_length=100,verbose_name='搜索内容')
#     search_time=models.DateTimeField(auto_now_add=True,verbose_name='搜索时间')




