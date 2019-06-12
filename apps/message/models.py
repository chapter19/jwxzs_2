from django.db import models
from ckeditor.fields import RichTextField,RichTextFormField
from ckeditor_uploader.fields import RichTextUploadingField
from datetime import datetime

from users.models import UserProfile,Class
from lessons.models import ScheduleLesson
from groups.models import Group
from disks.models import File



class Message(models.Model):
    type=models.IntegerField(choices=((1,'系统通知'),(2,'作业通知'),(3,'普通消息'),(4,'教务通知'),(5,'通知回复')),verbose_name='消息类型',default=3)
    sender=models.ForeignKey(UserProfile,verbose_name='发送人',help_text='发送人',related_name='send_message')
    title=models.CharField(max_length=100,verbose_name='标题',help_text='标题',default='')
    body=RichTextUploadingField(verbose_name='消息内容',default='',null=True,blank=True)
    send_time=models.DateTimeField(default=datetime.now, verbose_name=u'发送时间')
    reply_message=models.ForeignKey('self',null=True,blank=True,verbose_name='父消息',default=None)
    send_state=models.IntegerField(verbose_name='发送状态',choices=((0,'草稿'),(1,'发送')),default=1)
    # report_time = models.IntegerField(default=0, verbose_name='举报次数')
    if_report_over=models.BooleanField(verbose_name='是否被举报过度',default=False)
    if_delete = models.BooleanField(verbose_name='是否回收', default=False)
    if_collect = models.BooleanField(verbose_name='是否收藏', default=False)
    # update_time=models.DateTimeField(verbose_name='更新时间',blank=True,null=True)
    add_time = models.DateTimeField(default=datetime.now, verbose_name=u'添加时间')
    # message_receiver=models.ManyToManyField(ReceiverMessage,related_name='message',verbose_name='接收人',help_text='接收人')
    # message_receiver_group=models.ManyToManyField(ReceiverGroup,related_name='message',verbose_name='接收组',help_text='接收组')
    # file=models.ManyToManyField(MessageFile,related_name='message',verbose_name='文件',help_text='文件')

    def if_root(self):
        if self.reply_message:
            return False
        else:
            return True
    if_root.short_description='是否为根消息'

    # def send_num(self):
    #     return self.message_receiver.count()
    # send_num.short_description='接收人数'

    # def read_num(self):
    #     return self.message_receiver.filter(read_time__isnull=False).count()
    # read_num.short_description='已读人数'

    class Meta:
        verbose_name='消息'
        verbose_name_plural=verbose_name

    def __str__(self):
        return self.title


# 消息文件
class MessageFile(models.Model):
    message=models.ForeignKey(Message,related_name='message_file',verbose_name='消息',null=True,blank=True)
    # file_name=models.CharField(max_length=70,verbose_name='文件名',default='')
    # file = models.FileField(verbose_name='文件', upload_to="uploads_file/%Y/%m/%d")
    disk_file=models.ForeignKey(File,verbose_name='硬盘文件',related_name='message_file')
    add_time = models.DateTimeField(default=datetime.now, verbose_name=u'添加时间')
    def get_sender(self):
        return self.message.sender.name
    get_sender.short_description='发送人'
    # def get_receiver(self):
    #     return self.message.receiver_message.receiver.name
    # get_receiver.short_description = '接收人'
    class Meta:
        verbose_name='消息文件'
        verbose_name_plural=verbose_name
    def __str__(self):
        return self.disk_file.name


#接受组织
class ReceiverGroup(models.Model):
    message = models.ForeignKey(Message, related_name='receiver_group', verbose_name='消息',default=1)
    # group_type = models.IntegerField(choices=((1, '课程班级'), (2, '班级'), (3, '学院'), (4, '专业')), verbose_name='组织类型',default=1)
    # group_id = models.CharField(max_length=20, verbose_name='组织id',default='')
    # group_name=models.CharField(max_length=60,verbose_name='组织名',null=True,blank=True)
    group=models.ForeignKey(Group,related_name='receiver_group',verbose_name='组织',default=1)
    add_time = models.DateTimeField(default=datetime.now, verbose_name=u'添加时间')
    class Meta:
        verbose_name='消息接收组'
        verbose_name_plural=verbose_name
        unique_together=('message','group',)
    def __str__(self):
        return self.group.group_name


#接收组织接收人消息
class GroupReceiverMessage(models.Model):
    receiver_group=models.ForeignKey(ReceiverGroup,verbose_name='接收组',help_text='接收组',related_name='group_receiver_message',blank=True,null=True,on_delete=models.CASCADE)
    receiver = models.ForeignKey(UserProfile, verbose_name='接收人', help_text='接收人')
    read_time = models.DateTimeField(verbose_name='阅读时间', null=True, blank=True, default=None)
    if_delete = models.BooleanField(verbose_name='是否回收', default=False)
    if_collect = models.BooleanField(verbose_name='是否收藏', default=False)
    if_report=models.BooleanField(verbose_name='是否举报',default=False)
    add_time = models.DateTimeField(default=datetime.now, verbose_name=u'添加时间')
    def if_read(self):
        if self.read_time:
            return True
        else:
            return False
    if_read.short_description = '是否已读'
    class Meta:
        verbose_name = '接收组接收人消息'
        verbose_name_plural = verbose_name
    def __str__(self):
        return self.receiver.username


#接收人消息
class ReceiverMessage(models.Model):
    message = models.ForeignKey(Message, related_name='receiver_message', verbose_name='消息', null=True, blank=True)
    receiver=models.ForeignKey(UserProfile,verbose_name='接收人',help_text='接收人',related_name='receiver_message')
    read_time = models.DateTimeField(verbose_name='阅读时间', null=True, blank=True,default=None)
    if_delete=models.BooleanField(verbose_name='是否回收',default=False)
    if_collect=models.BooleanField(verbose_name='是否收藏',default=False)
    if_report=models.BooleanField(verbose_name='是否举报',default=False)
    add_time = models.DateTimeField(default=datetime.now, verbose_name=u'添加时间')
    def get_sender(self):
        return self.message.sender.name
    get_sender.short_description='发送人'
    def if_read(self):
        if self.read_time:
            return True
        else:
            return False
    if_read.short_description='是否已读'
    class Meta:
        verbose_name='接收人消息'
        verbose_name_plural=verbose_name
        unique_together=('message','receiver',)
    def __str__(self):
        return self.receiver.username
















