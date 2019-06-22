from django.db import models
import uuid
from datetime import datetime

from users.models import UserProfile


class UpdateLog(models.Model):
    verbose_id=models.UUIDField(default=uuid.uuid4(),verbose_name='第二个的id')
    url=models.CharField(max_length=200,verbose_name='URL',blank=True,null=True)
    task_id=models.CharField(max_length=70,verbose_name='任务id',blank=True,null=True)
    desc=models.CharField(max_length=200,verbose_name='描述',default='')
    class_and_method=models.CharField(max_length=200,verbose_name='调用的类和方法',default='')
    start_time=models.DateTimeField(default=datetime.now,verbose_name='开始时间')
    type=models.CharField(choices=(('Graduate','毕业生失效'),('Neo4j','Neo4j图数据库')),max_length=16,verbose_name='类型',blank=True,null=True)
    stop_time=models.DateTimeField(verbose_name='结束时间',blank=True,null=True)
    status=models.CharField(max_length=8,choices=(('getting','正在更新'),('end','更新结束'),('error','更新异常'),('retried','已重试'),('stopped','已终止')),default='getting',verbose_name='状态')
    user=models.ForeignKey(UserProfile,verbose_name='操作人',blank=True,null=True)
    class Meta:
        verbose_name='更新日志'
        verbose_name_plural=verbose_name
    def __str__(self):
        return self.desc
