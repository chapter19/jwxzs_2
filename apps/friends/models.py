from django.db import models
from users.models import UserProfile
from datetime import datetime


class CollectFriends(models.Model):
    user=models.ForeignKey(UserProfile,verbose_name='用户',related_name='my_collect_friends')
    friend=models.ForeignKey(UserProfile,verbose_name='好友',related_name='who_collect_me')
    # last_talk=models.DateTimeField(default=datetime.now,verbose_name='上一次联系时间')
    add_time=models.DateTimeField(default=datetime.now,verbose_name='添加时间')
    class Meta:
        verbose_name='收藏好友'
        verbose_name_plural=verbose_name
        unique_together=('user','friend',)
    def __str__(self):
        return self.friend.name


class RecentContact(models.Model):
    user=models.ForeignKey(UserProfile,verbose_name='用户',related_name='my_contact')
    contact=models.ForeignKey(UserProfile,verbose_name='最近联系人',related_name='who_contact_me')
    add_time = models.DateTimeField(default=datetime.now, verbose_name='添加时间')
    class Meta:
        verbose_name = '最近联系人'
        verbose_name_plural = verbose_name
        unique_together=('user','contact',)
    def __str__(self):
        return self.contact.name


