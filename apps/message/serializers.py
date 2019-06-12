#-*- coding:utf-8 -*-
from rest_framework import serializers
from .models import Message,ReceiverMessage,MessageFile,ReceiverGroup,GroupReceiverMessage
from rest_framework_recursive.fields import RecursiveField
# from users.serializer import UserProfileSerializer
from users.models import UserProfile,Class,Colloge,Major
from lessons.models import ScheduleLesson,Lesson
from datetime import datetime
from groups.models import Group,GroupAdministrator,DefGroup,DefGroupMember
from groups.models import Group
from friends.models import RecentContact
from django.db.models import Q

from disks.serializers import FileListSerializer
from disks.models import File


#发件箱
class ReceiverSerializer(serializers.ModelSerializer):
    class Meta:
        model=UserProfile
        fields=['username','name','id']


class OutboxGroupReceiverSerializer(serializers.ModelSerializer):
    receiver = ReceiverSerializer()
    read_time = serializers.DateTimeField(read_only=True, format='%Y-%m-%d %H:%M')
    class Meta:
        model=GroupReceiverMessage
        fields=['receiver','read_time','id']


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model=Group
        fields=['group_type','group_name','group_id','id']


class OutboxGroupSerializer(serializers.ModelSerializer):
    group_receiver_message=OutboxGroupReceiverSerializer(many=True)
    group=GroupSerializer()
    class Meta:
        model=ReceiverGroup
        fields=['group_receiver_message','group','id']


class OutboxReceiverMessageSerializer(serializers.ModelSerializer):
    receiver=ReceiverSerializer()
    read_time=serializers.DateTimeField(read_only=True,format='%Y-%m-%d %H:%M')
    class Meta:
        model=ReceiverMessage
        fields=['read_time','receiver','id']


class MessageFileSerializer(serializers.ModelSerializer):
    disk_file=FileListSerializer()
    class Meta:
        model=MessageFile
        fields='__all__'


class OutboxReplyMessageSerializer(serializers.ModelSerializer):
    # receive_group=OutboxGroupSerializer()
    # receiver_mess
    receiver_message=OutboxReceiverMessageSerializer(many=True)
    receiver_group=OutboxGroupSerializer(many=True)
    # sender=ReceiverSerializer()
    message_file=MessageFileSerializer(many=True)
    send_time=serializers.DateTimeField(read_only=True,format='%Y-%m-%d %H:%M')
    class Meta:
        model=Message
        fields=['receiver_message','receiver_group','title','body','send_time','if_delete','if_collect','message_file','id']


class OutboxMessageSerializer(serializers.ModelSerializer):
    # receive_group=OutboxGroupSerializer()
    # receiver_mess
    receiver_message=OutboxReceiverMessageSerializer(many=True)
    receiver_group=OutboxGroupSerializer(many=True)
    # sender=ReceiverSerializer()
    reply_message=OutboxReplyMessageSerializer()
    message_file=MessageFileSerializer(many=True)
    send_time=serializers.DateTimeField(read_only=True,format='%Y-%m-%d %H:%M',help_text='发送时间')
    class Meta:
        model=Message
        fields=['receiver_message','receiver_group','title','body','send_time','if_delete','if_collect','message_file','reply_message','id']


#发件
class OutboxMessageCreateSerializer(serializers.ModelSerializer):
    id=serializers.IntegerField(read_only=True)
    user_id=serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    # reply_message_id=serializers.IntegerField(required=False,help_text='回复的父消息')
    title=serializers.CharField(required=False,help_text='标题',label='标题')
    type=serializers.ChoiceField(choices=((1,'系统通知'),(2,'作业通知'),(3,'普通消息'),(4,'教务通知'),(5,'通知回复')),required=False,default=3,label='消息类型',help_text='消息类型')
    class Meta:
        model=Message
        fields=['id','user_id','reply_message','title','body','send_state','type']
    def create(self, validated_data):
        title=validated_data.get('title')
        user_id=validated_data.get('user_id')
        send_state=0
        reply_message=validated_data.get('reply_message')
        body=validated_data.get('body')
        type=validated_data.get('type')
        if reply_message:
            re_me=ReceiverMessage.objects.filter(message=reply_message,receiver_id=user_id)
            if not re_me:
                gr_re_me=GroupReceiverMessage.objects.filter(receiver_group__message=reply_message,receiver_id=user_id)
                if not gr_re_me:
                    raise serializers.ValidationError({'detail':'你没有收到该消息！不能回复该消息'})
            if reply_message.title[:3]=='回复：':
                t=reply_message.title
            else:
                t='回复：'+reply_message.title
            if title:
                title=t+'    ' + title
            else:
                title=t
            if reply_message.type in [1,2,4]:
                type=5
            else:
                type=3
            obj = Message.objects.create(title=title, sender_id=user_id, send_state=send_state,reply_message=reply_message,body=body,type=type)
            ReceiverMessage.objects.create(message=obj, receiver=reply_message.sender)
            return obj
        if title:
            user=UserProfile.objects.get(id=user_id)
            if user.is_student:
                if type in [1,2,4]:
                    raise serializers.ValidationError({'detail':'你不能发送该类消息！'})
            obj = Message.objects.create(title=title, sender_id=user_id, send_state=send_state,body=body,type=type)
            return obj
        else:
            raise serializers.ValidationError({'detail':'你忘了填写标题！'})


#改件
class OutboxMessageUpdateSerializer(serializers.ModelSerializer):
    id=serializers.IntegerField(read_only=True)
    user_id=serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    title=serializers.CharField(required=True,help_text='标题')
    body=serializers.CharField(required=True,help_text='内容')
    class Meta:
        model=Message
        fields=['title','body','user_id','id','type','send_state','reply_message']
    def update(self, instance, validated_data):
        user_id=validated_data.get('user_id')
        if instance.send_state==0:
            instance.title = validated_data.get('title', instance.title)
            instance.body = validated_data.get('body', instance.body)
            instance.send_state = validated_data.get('send_state', instance.send_state)
            instance.type = validated_data.get('type', instance.type)
            reply_message=validated_data.get('reply_message')
            if reply_message:
                re_me = ReceiverMessage.objects.filter(message=reply_message, receiver_id=user_id)
                if not re_me:
                    gr_re_me = GroupReceiverMessage.objects.filter(receiver_group__message=reply_message,receiver_id=user_id)
                    if not gr_re_me:
                        raise serializers.ValidationError({'detail': '你没有收到该消息！不能回复该消息'})
                if reply_message.type in [1, 2, 4]:
                    type = 5
                else:
                    type = 3
                instance.type=type
                instance.reply_message=reply_message
            if not instance.reply_message:
                user = UserProfile.objects.get(id=user_id)
                if user.is_student:
                    if instance.type in [1, 2, 4]:
                        raise serializers.ValidationError({'detail': '你不能发送该类消息！'})
            instance.send_time = datetime.now
            instance.save()
            return instance
        else:
            raise serializers.ValidationError({'detail':'已发送信息不能修改！'})


#上传文件
class OutboxMessageFileCreateSerializer(serializers.ModelSerializer):
    id=serializers.IntegerField(read_only=True,help_text='文件id',label='文件id')
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    class Meta:
        model=MessageFile
        fields=['message','disk_file','id','user']
    def create(self, validated_data):
        message=validated_data.get('message')
        u = validated_data.get('user')
        if message.sender_id==u:
            if message.send_state==1:
                raise serializers.ValidationError({'detail':'已发送该消息！不能添加文件！'})
            disk_file=validated_data.get('disk_file')
            if disk_file.if_delete:
                raise serializers.ValidationError({'detail':'该文件已被回收！不能选择'})
            disk=disk_file.disk
            if disk.if_disable:
                raise serializers.ValidationError({'detail':'你的网盘已被禁用，不能再继续使用！'})
            if disk.if_close:
                raise serializers.ValidationError({'detail':'你已经关闭了网盘！先去开启再继续使用吧'})
            if disk_file.disk.ower_id==u:
                mes_file=MessageFile(message=message,disk_file=disk_file)
                mes_file.save()
                return mes_file
            else:
                raise serializers.ValidationError({'detail':'你不能使用别人的文件！'})
        else:
            raise serializers.ValidationError({'detail':"当前用户不是发件人，没有权限上传文件！"})


#更改上传文件
# class OutboxMessageFileUpdateSerializer(serializers.Serializer):
#     file_name=serializers.CharField(help_text='文件名')
#     file=serializers.FileField(help_text='文件')
#     def update(self, instance, validated_data):
#         instance.file_name=validated_data.get('file_name',instance.file_name)
#         instance.file=validated_data.get('file',instance.file)
#         instance.save()
#         return instance
#     class Meta:
#         model=MessageFile
#         fields=['message_id','file_name','file','id','user']


#创建接受者
class OutboxMessageReceiverCreateSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    def create(self, validated_data):
        message=validated_data.get('message')
        u = validated_data.get('user')
        if message.sender_id==u:
            if message.send_state==1:
                raise serializers.ValidationError({'detail':'已发送该消息！不能添加接收者！'})
            receiver=validated_data.get('receiver')
            mes_receiver = ReceiverMessage.objects.filter(message=message,receiver=receiver)
            if mes_receiver:
                raise serializers.ValidationError({'detail':'已向该用户发送消息，勿重复发送！'})
            mes_receiver = ReceiverMessage.objects.create(message=message, receiver=receiver)
            contact=RecentContact.objects.filter(user_id=u,contact=receiver)
            if contact:
                contact=contact[0]
                contact.add_time=datetime.now()
                contact.save()
            else:
                RecentContact.objects.create(user_id=u,contact=receiver)
            return mes_receiver
        else:
            raise serializers.ValidationError({'detail':"你不是发件人，没有权限发送该消息给他人！"})
    class Meta:
        model=ReceiverMessage
        fields=['message','receiver','user','id']



# 接收组创建
class OutboxGroupCreateSerializer(serializers.ModelSerializer):
    id=serializers.IntegerField(read_only=True)
    # group_name=serializers.CharField(read_only=True,help_text='组织名称')
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    # group=serializers.CharField(required=True,help_text='组织的id',label='组织id')
    class Meta:
        model=ReceiverGroup
        fields=['message','user','group','id']
    def create(self, validated_data):
        user=validated_data.get('user')
        message=validated_data.get('message')
        if message.sender_id==user:
            if message.send_state==1:
                raise serializers.ValidationError({'detail':'已发送该消息！不能添加接受者！'})
            group=validated_data.get('group')
            ad=GroupAdministrator.objects.filter(admin=user,group=group)
            if ad:
                group_rece = ReceiverGroup.objects.filter(group=group, message=message)
                if group_rece:
                    raise serializers.ValidationError({'detail':'已添加该群组！不能再添加发送'})
                group_rece=ReceiverGroup.objects.create(group=group,message=message)
                if group[0].group_type==1:
                    group_receivers = UserProfile.objects.filter(student__score__schedule_lesson_id=group.group_id)
                    for i in group_receivers:
                        GroupReceiverMessage.objects.create(receiver_group=group_rece,receiver=i)
                elif group[0].group_type==2:
                    group_receivers=UserProfile.objects.filter(student__cla_id=group.group_id)
                    for i in group_receivers:
                        GroupReceiverMessage.objects.create(receiver_group=group_rece,receiver=i)
                elif group[0].group_type==3:
                    group_receivers=UserProfile.objects.filter(student__cla__colloge_id=group.group_id)
                    for i in group_receivers:
                        GroupReceiverMessage.objects.create(receiver_group=group_rece,receiver=i)
                elif group[0].group_type==4:
                    group_receivers=UserProfile.objects.filter(student__cla__major_id=group.group_id)
                    for i in group_receivers:
                        GroupReceiverMessage.objects.create(receiver_group=group_rece,receiver=i)
                else:
                    raise serializers.ValidationError({'detail':'找不到组织类型！'})
                return group_rece
            else:
                if group.group_type==5:
                    def_g=DefGroup.objects.filter(def_group_member=user,id=group.group_id)
                    if def_g:
                        group_rece=ReceiverGroup.objects.create(group=def_g[0],message=message)
                        group_receivers=UserProfile.objects.filter(def_group_member__def_group=def_g[0])
                        for i in group_receivers:
                            if i.id!=user:
                                GroupReceiverMessage.objects.create(receiver_group=group_rece,receiver=i)
                        return group_rece
                    else:
                        raise serializers.ValidationError({'detail':'你不是该组组员！不能添加'})
                        # group_receivers=UserProfile.objects.filter()
                else:
                    raise serializers.ValidationError({'detail':'你不是该组织管理员，没有权限群发消息！'})
        else:
            raise serializers.ValidationError({'detail':'你不是该消息发送者，没有权限发送当前消息！'})

#收件箱
#已读、收藏、删除
class InboxMessageReceiverUpdateSerializer(serializers.Serializer):
    id=serializers.IntegerField(read_only=True)
    if_read=serializers.BooleanField(required=False,help_text='标记是否已读',write_only=True)
    if_delete=serializers.BooleanField(required=False,help_text='是否回收')
    if_collect=serializers.BooleanField(required=False,help_text='是否收藏')
    if_report=serializers.BooleanField(required=False,help_text='是否举报')
    # read_time = serializers.HiddenField()
    # user = serializers.HiddenField(
    #     default=serializers.CurrentUserDefault()
    # )
    def update(self, instance, validated_data):
        instance.if_delete=validated_data.get('if_delete',instance.if_delete)
        instance.if_collect=validated_data.get('if_collect',instance.if_collect)
        instance.if_report=validated_data.get('if_report',instance.if_report)
        if validated_data.get('if_read'):
            # ReceiverMessage
            if instance.read_time:
                pass
            else:
                instance.read_time=datetime.now()
        # instance.send_time = datetime.now()
        instance.save()
        id = validated_data.get('id')
        mess = Message.objects.get(receiver_message__id=id)
        repo_time = ReceiverMessage.objects.filter(message=mess,if_report=True).count() + GroupReceiverMessage.objects.filter(receiver_group__message=mess, if_report=True).count()
        if repo_time > 5:
            mess.if_report_over = True
            mess.save()
        return instance
    class Meta:
        model=ReceiverMessage
        fields=['id','read_time','if_delete','if_collect','if_read','if_report']


#群组收件箱
#已读、收藏、删除
class InboxGroupReceiverUpdateSerializer(serializers.Serializer):
    id=serializers.IntegerField(read_only=True)
    if_read=serializers.BooleanField(required=False,help_text='标记是否已读',write_only=True)
    if_delete=serializers.BooleanField(required=False,help_text='是否回收')
    if_collect=serializers.BooleanField(required=False,help_text='是否收藏')
    if_report=serializers.BooleanField(required=False,help_text='是否举报')
    # read_time = serializers.HiddenField()
    # user = serializers.HiddenField(
    #     default=serializers.CurrentUserDefault()
    # )
    def update(self, instance, validated_data):
        instance.if_delete=validated_data.get('if_delete',instance.if_delete)
        instance.if_collect=validated_data.get('if_collect',instance.if_collect)
        instance.if_report=validated_data.get('if_report',instance.if_report)
        if validated_data.get('if_read'):
            # ReceiverMessage
            if instance.read_time:
                pass
            else:
                instance.read_time=datetime.now()
        # instance.send_time = datetime.now()
        instance.save()
        id = validated_data.get('id',instance.id)
        mess = Message.objects.get(receiver_group__group_receiver_message__id=id)
        repo_time=ReceiverMessage.objects.filter(message=mess,if_report=True).count()+GroupReceiverMessage.objects.filter(receiver_group__message=mess,if_report=True).count()
        if repo_time>5:
            mess.if_report_over=True
            mess.save()
        return instance
    class Meta:
        model=GroupReceiverMessage
        fields=['id','read_time','if_delete','if_collect','if_read','if_report']


#收件箱列表
class InboxMessageSerializer(serializers.ModelSerializer):
    receiver_message=OutboxReceiverMessageSerializer(many=True)
    receiver_group=OutboxGroupSerializer(many=True)
    sender=ReceiverSerializer()
    reply_message=OutboxReplyMessageSerializer()
    message_file=MessageFileSerializer(many=True)
    send_time=serializers.DateTimeField(read_only=True,format='%Y-%m-%d %H:%M',help_text='发送时间')
    class Meta:
        model=Message
        fields=['receiver_message','receiver_group','title','body','send_time','if_delete','if_collect','message_file','reply_message']

class ReceiverUpdateByQuerySerailizer(serializers.Serializer):
    user_id=serializers.HiddenField(default=serializers.CurrentUserDefault())
    delete_id_list=serializers.ListField(child=serializers.IntegerField(),required=False,allow_null=True,allow_empty=True,write_only=True,label='收件人要回收的消息的id列表',help_text='收件人要回收的消息的id列表')
    resume_id_list=serializers.ListField(child=serializers.IntegerField(),required=False,allow_null=True,allow_empty=True,write_only=True,label='收件人要恢复的消息的id列表',help_text='收件人要恢复的消息的id列表')
    collect_id_list=serializers.ListField(child=serializers.IntegerField(),required=False,allow_null=True,allow_empty=True,write_only=True,label='收件人要收藏的消息的id列表',help_text='收件人要收藏的消息的id列表')
    no_collect_id_list=serializers.ListField(child=serializers.IntegerField(),required=False,allow_null=True,allow_empty=True,write_only=True,label='收件人要取消收藏的消息的id列表',help_text='收件人要取消收藏的消息的id列表')
    report_id_list=serializers.ListField(child=serializers.IntegerField(),required=False,allow_null=True,allow_empty=True,write_only=True,label='收件人要举报的消息的id列表',help_text='收件人要举报的消息的id列表')
    read_id_list=serializers.ListField(child=serializers.IntegerField(),required=False,allow_null=True,allow_empty=True,write_only=True,label='收件人要标记已读的消息的id列表',help_text='收件人要标记已读的消息的id列表')
    no_read_id_list=serializers.ListField(child=serializers.IntegerField(),required=False,allow_null=True,allow_empty=True,write_only=True,label='收件人要标记未读的消息的id列表',help_text='收件人要标记未读的消息的id列表')
    def create(self, validated_data):
        user_id=validated_data.get('user_id')
        delete_id_list=validated_data.get('delete_id_list')
        if delete_id_list:
            for id in delete_id_list:
                receiver_message=ReceiverMessage.objects.filter(message_id=id,receiver_id=user_id)
                if receiver_message:
                    receiver_message=receiver_message[0]
                    if receiver_message.if_delete:
                        raise serializers.ValidationError({'detail':'该消息已回收！不能重复回收！'})
                    receiver_message.if_delete=True
                    receiver_message.save()
                else:
                    raise serializers.ValidationError({'detail':'消息不存在！'})
        resume_id_list = validated_data.get('resume_id_list')
        if resume_id_list:
            for id in resume_id_list:
                receiver_message = ReceiverMessage.objects.filter(message_id=id, receiver_id=user_id)
                if receiver_message:
                    receiver_message = receiver_message[0]
                    if not receiver_message.if_delete:
                        raise serializers.ValidationError({'detail': '该消息未回收！不能恢复！'})
                    receiver_message.if_delete = False
                    receiver_message.save()
                else:
                    raise serializers.ValidationError({'detail': '消息不存在！'})
        collect_id_list=validated_data.get('collect_id_list')
        if collect_id_list:
            for id in collect_id_list:
                receiver_message = ReceiverMessage.objects.filter(message_id=id, receiver_id=user_id)
                if receiver_message:
                    receiver_message = receiver_message[0]
                    if receiver_message.if_collect:
                        raise serializers.ValidationError({'detail': '该消息已收藏！不能重复收藏！'})
                    receiver_message.if_collect = True
                    receiver_message.save()
                else:
                    raise serializers.ValidationError({'detail': '消息不存在！'})
        no_collect_id_list=validated_data.get('no_collect_id_list')
        if no_collect_id_list:
            for id in no_collect_id_list:
                receiver_message = ReceiverMessage.objects.filter(message_id=id, receiver_id=user_id)
                if receiver_message:
                    receiver_message = receiver_message[0]
                    if not receiver_message.if_collect:
                        raise serializers.ValidationError({'detail': '该消息未收藏！不能取消收藏！'})
                    receiver_message.if_collect = False
                    receiver_message.save()
                else:
                    raise serializers.ValidationError({'detail': '消息不存在！'})
        report_id_list = validated_data.get('report_id_list')
        if report_id_list:
            for id in report_id_list:
                receiver_message = ReceiverMessage.objects.filter(message_id=id, receiver_id=user_id)
                if receiver_message:
                    receiver_message = receiver_message[0]
                    if receiver_message.if_report:
                        raise serializers.ValidationError({'detail': '该消息已举报！不能重复举报！'})
                    receiver_message.if_report = True
                    receiver_message.save()
                else:
                    raise serializers.ValidationError({'detail': '消息不存在！'})
        read_id_list = validated_data.get('read_id_list')
        if read_id_list:
            for id in read_id_list:
                receiver_message = ReceiverMessage.objects.filter(message_id=id, receiver_id=user_id)
                if receiver_message:
                    receiver_message = receiver_message[0]
                    if receiver_message.read_time!=None:
                        raise serializers.ValidationError({'detail': '该消息已阅读！不能重复标记为已读！'})
                    receiver_message.read_time=datetime.now()
                    receiver_message.save()
                else:
                    raise serializers.ValidationError({'detail': '消息不存在！'})
        no_read_id_list = validated_data.get('no_read_id_list')
        if no_read_id_list:
            for id in no_read_id_list:
                receiver_message = ReceiverMessage.objects.filter(message_id=id, receiver_id=user_id)
                if receiver_message:
                    receiver_message = receiver_message[0]
                    if receiver_message.read_time == None:
                        raise serializers.ValidationError({'detail': '该消息未读！不能标记为未读！'})
                    receiver_message.read_time = None
                    receiver_message.save()
                else:
                    raise serializers.ValidationError({'detail': '消息不存在！'})
        return {'detail': '批量操作成功！'}


class GroupReceiverUpdateByQuerySerailizer(serializers.Serializer):
    user_id=serializers.HiddenField(default=serializers.CurrentUserDefault())
    delete_id_list=serializers.ListField(child=serializers.IntegerField(),required=False,allow_null=True,allow_empty=True,write_only=True,label='收件人要回收的消息的id列表',help_text='收件人要回收的消息的id列表')
    resume_id_list=serializers.ListField(child=serializers.IntegerField(),required=False,allow_null=True,allow_empty=True,write_only=True,label='收件人要恢复的消息的id列表',help_text='收件人要恢复的消息的id列表')
    collect_id_list=serializers.ListField(child=serializers.IntegerField(),required=False,allow_null=True,allow_empty=True,write_only=True,label='收件人要收藏的消息的id列表',help_text='收件人要收藏的消息的id列表')
    no_collect_id_list=serializers.ListField(child=serializers.IntegerField(),required=False,allow_null=True,allow_empty=True,write_only=True,label='收件人要取消收藏的消息的id列表',help_text='收件人要取消收藏的消息的id列表')
    report_id_list=serializers.ListField(child=serializers.IntegerField(),required=False,allow_null=True,allow_empty=True,write_only=True,label='收件人要举报的消息的id列表',help_text='收件人要举报的消息的id列表')
    read_id_list = serializers.ListField(child=serializers.IntegerField(), required=False, allow_null=True,
                                         allow_empty=True, write_only=True, label='收件人要标记已读的消息的id列表',
                                         help_text='收件人要标记已读的消息的id列表')
    no_read_id_list = serializers.ListField(child=serializers.IntegerField(), required=False, allow_null=True,
                                            allow_empty=True, write_only=True, label='收件人要标记未读的消息的id列表',
                                            help_text='收件人要标记未读的消息的id列表')
    def create(self, validated_data):
        user_id=validated_data.get('user_id')
        delete_id_list=validated_data.get('delete_id_list')
        if delete_id_list:
            for id in delete_id_list:
                receiver_message=GroupReceiverMessage.objects.filter(receiver_group__message_id=id,receiver_id=user_id)
                if receiver_message:
                    receiver_message=receiver_message[0]
                    if receiver_message.if_delete:
                        raise serializers.ValidationError({'detail':'该消息已回收！不能重复回收！'})
                    receiver_message.if_delete=True
                    receiver_message.save()
                else:
                    raise serializers.ValidationError({'detail':'消息不存在！'})
        resume_id_list = validated_data.get('resume_id_list')
        if resume_id_list:
            for id in resume_id_list:
                receiver_message = GroupReceiverMessage.objects.filter(receiver_group__message_id=id, receiver_id=user_id)
                if receiver_message:
                    receiver_message = receiver_message[0]
                    if not receiver_message.if_delete:
                        raise serializers.ValidationError({'detail': '该消息未回收！不能恢复！'})
                    receiver_message.if_delete = False
                    receiver_message.save()
                else:
                    raise serializers.ValidationError({'detail': '消息不存在！'})
        collect_id_list=validated_data.get('collect_id_list')
        if collect_id_list:
            for id in collect_id_list:
                receiver_message = GroupReceiverMessage.objects.filter(receiver_group__message_id=id,
                                                                       receiver_id=user_id)
                if receiver_message:
                    receiver_message = receiver_message[0]
                    if receiver_message.if_collect:
                        raise serializers.ValidationError({'detail': '该消息已收藏！不能重复收藏！'})
                    receiver_message.if_collect = True
                    receiver_message.save()
                else:
                    raise serializers.ValidationError({'detail': '消息不存在！'})
        no_collect_id_list=validated_data.get('no_collect_id_list')
        if no_collect_id_list:
            for id in no_collect_id_list:
                receiver_message = GroupReceiverMessage.objects.filter(receiver_group__message_id=id,
                                                                       receiver_id=user_id)
                if receiver_message:
                    receiver_message = receiver_message[0]
                    if not receiver_message.if_collect:
                        raise serializers.ValidationError({'detail': '该消息未收藏！不能取消收藏！'})
                    receiver_message.if_collect = False
                    receiver_message.save()
                else:
                    raise serializers.ValidationError({'detail': '消息不存在！'})
        report_id_list = validated_data.get('report_id_list')
        if report_id_list:
            for id in report_id_list:
                receiver_message = GroupReceiverMessage.objects.filter(receiver_group__message_id=id,
                                                                       receiver_id=user_id)
                if receiver_message:
                    receiver_message = receiver_message[0]
                    if receiver_message.if_report:
                        raise serializers.ValidationError({'detail': '该消息已举报！不能重复举报！'})
                    receiver_message.if_report = True
                    receiver_message.save()
                else:
                    raise serializers.ValidationError({'detail': '消息不存在！'})
        read_id_list = validated_data.get('read_id_list')
        if read_id_list:
            for id in read_id_list:
                receiver_message = GroupReceiverMessage.objects.filter(receiver_group__message_id=id,
                                                                       receiver_id=user_id)
                if receiver_message:
                    receiver_message = receiver_message[0]
                    if receiver_message.read_time!=None:
                        raise serializers.ValidationError({'detail': '该消息已读！不能重复标记为已读！'})
                    receiver_message.read_time=datetime.now()
                    receiver_message.save()
                else:
                    raise serializers.ValidationError({'detail': '消息不存在！'})
        no_read_id_list = validated_data.get('no_read_id_list')
        if no_read_id_list:
            for id in no_read_id_list:
                receiver_message = GroupReceiverMessage.objects.filter(receiver_group__message_id=id,
                                                                       receiver_id=user_id)
                if receiver_message:
                    receiver_message = receiver_message[0]
                    if receiver_message.read_time == None:
                        raise serializers.ValidationError({'detail': '该消息未读！不能标记为未读！'})
                    receiver_message.read_time = None
                    receiver_message.save()
                else:
                    raise serializers.ValidationError({'detail': '消息不存在！'})
        return {'detail': '批量操作成功！'}

class SenderUpdateByQuerySerializer(serializers.Serializer):
    user_id = serializers.HiddenField(default=serializers.CurrentUserDefault())
    delete_id_list = serializers.ListField(child=serializers.IntegerField(), required=False, allow_null=True,
                                           allow_empty=True, write_only=True, label='发件人要回收的消息的id列表',
                                           help_text='发件人要回收的消息的id列表')
    resume_id_list = serializers.ListField(child=serializers.IntegerField(), required=False, allow_null=True,
                                           allow_empty=True, write_only=True, label='发件人要恢复的消息的id列表',
                                           help_text='发件人要恢复的消息的id列表')
    collect_id_list = serializers.ListField(child=serializers.IntegerField(), required=False, allow_null=True,
                                            allow_empty=True, write_only=True, label='发件人要收藏的消息的id列表',
                                            help_text='发件人要收藏的消息的id列表')
    no_collect_id_list = serializers.ListField(child=serializers.IntegerField(), required=False, allow_null=True,
                                               allow_empty=True, write_only=True, label='发件人要取消收藏的消息的id列表',
                                               help_text='发件人要取消收藏的消息的id列表')
    def create(self, validated_data):
        user_id = validated_data.get('user_id')
        delete_id_list = validated_data.get('delete_id_list')
        if delete_id_list:
            for id in delete_id_list:
                message=Message.objects.filter(id=id)
                if message:
                    message=message[0]
                    if message.sender_id!=user_id:
                        raise serializers.ValidationError({'detail':'你不能修改别人的消息！'})
                    if message.if_delete:
                        raise serializers.ValidationError({'detail':'该消息已回收！不要重复回收'})
                    message.if_delete=True
                    message.save()
                else:
                    raise serializers.ValidationError({'detail':'消息不存在！'})
        resume_id_list = validated_data.get('resume_id_list')
        if resume_id_list:
            for id in resume_id_list:
                message = Message.objects.filter(id=id)
                if message:
                    message = message[0]
                    if message.sender_id != user_id:
                        raise serializers.ValidationError({'detail': '你不能修改别人的消息！'})
                    if not message.if_delete:
                        raise serializers.ValidationError({'detail': '该消息未回收！不能恢复！'})
                    message.if_delete = False
                    message.save()
                else:
                    raise serializers.ValidationError({'detail': '消息不存在！'})
        collect_id_list = validated_data.get('collect_id_list')
        if collect_id_list:
            for id in collect_id_list:
                message = Message.objects.filter(id=id)
                if message:
                    message = message[0]
                    if message.sender_id != user_id:
                        raise serializers.ValidationError({'detail': '你不能修改别人的消息！'})
                    if message.if_collect:
                        raise serializers.ValidationError({'detail': '该消息已收藏！不能重复收藏！'})
                    message.if_collect=True
                    message.save()
                else:
                    raise serializers.ValidationError({'detail': '消息不存在！'})
        no_collect_id_list = validated_data.get('no_collect_id_list')
        if no_collect_id_list:
            for id in resume_id_list:
                message = Message.objects.filter(id=id)
                if message:
                    message = message[0]
                    if message.sender_id != user_id:
                        raise serializers.ValidationError({'detail': '你不能修改别人的消息！'})
                    if not message.if_collect:
                        raise serializers.ValidationError({'detail': '该消息未收藏！不能取消收藏！'})
                    message.if_collect = False
                    message.save()
                else:
                    raise serializers.ValidationError({'detail': '消息不存在！'})
        return {'detail': '批量操作成功！'}


class OneKeyToReadSerializer(serializers.Serializer):
    user_id=serializers.HiddenField(default=serializers.CurrentUserDefault())
    def create(self, validated_data):
        user_id=validated_data.get('user_id')
        ReceiverMessage.objects.filter(receiver_id=user_id,read_time=None,message__send_state=1).update(read_time=datetime.now())
        GroupReceiverMessage.objects.filter(receiver_id=user_id,read_time=None,receiver_group__message__send_state=1).update(read_time=datetime.now())
        return {'detail': '一键已读成功！'}