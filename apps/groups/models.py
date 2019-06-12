from django.db import models
from users.models import UserProfile
# Create your models here.
from datetime import datetime

class Group(models.Model):
    group_type = models.IntegerField(choices=((1, '课程班级'), (2, '班级'), (3, '学院'), (4, '专业'),(5,'自定义')), verbose_name='组织类型',default=1)
    group_id = models.CharField(max_length=20, verbose_name='组织id', default='')
    group_name = models.CharField(max_length=60, verbose_name='组织名', null=True, blank=True)
    add_time=models.DateTimeField(verbose_name='添加时间',default=datetime.now)
    class Meta:
        verbose_name='组织'
        verbose_name_plural=verbose_name
    def __str__(self):
        return self.group_name


class GroupAdministrator(models.Model):
    admin=models.ForeignKey(UserProfile,verbose_name='管理员',on_delete=models.CASCADE,related_name='group_admin')
    if_super=models.BooleanField(verbose_name='是否为超级管理员',default=False)
    group=models.ForeignKey(Group,verbose_name='组织',on_delete=models.CASCADE,related_name='group_admin')
    add_time = models.DateTimeField(verbose_name='添加时间', default=datetime.now)
    class Meta:
        verbose_name='组织管理员'
        verbose_name_plural=verbose_name
    def __str__(self):
        return self.admin.name


class DefGroup(models.Model):
    creater=models.ForeignKey(UserProfile,verbose_name='创建者',related_name='create_def_group')
    name=models.CharField(max_length=70,verbose_name='组名',default='')
    add_time = models.DateTimeField(verbose_name='添加时间', default=datetime.now)
    group=models.OneToOneField(Group,verbose_name='对应的群组',blank=True,null=True,related_name='def_group')
    class Meta:
        verbose_name='自定义组'
        verbose_name_plural=verbose_name
        unique_together=('creater','name',)
    def __str__(self):
        return self.name


class DefGroupMember(models.Model):
    member=models.ForeignKey(UserProfile,verbose_name='成员',related_name='def_group_member')
    def_group=models.ForeignKey(DefGroup,verbose_name='组',related_name='def_group_member')
    add_time = models.DateTimeField(verbose_name='添加时间', default=datetime.now)
    class Meta:
        verbose_name='自定义组成员'
        verbose_name_plural=verbose_name
        unique_together=('member','def_group',)
    def __str__(self):
        return self.member.name





