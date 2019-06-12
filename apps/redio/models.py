from django.db import models
from ckeditor_uploader.fields import RichTextUploadingField

# Create your models here.

class Redio(models.Model):
    id=models.CharField(max_length=15,verbose_name='通知编号',help_text='通知编号',primary_key=True)
    title=models.CharField(max_length=100,verbose_name='标题',help_text='标题',default='')
    body=RichTextUploadingField(verbose_name='内容',help_text='内容',default='')
    time=models.DateTimeField(verbose_name='发布时间',help_text='发布时间',default='')
    add_time=models.DateTimeField(auto_now_add=True,verbose_name='添加时间',help_text='添加时间')
    class Meta:
        verbose_name='教务通知'
        verbose_name_plural=verbose_name
    def __str__(self):
        return self.title












