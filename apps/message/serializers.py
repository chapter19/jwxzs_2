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


#发件箱
class ReceiverSerializer(serializers.ModelSerializer):
    class Meta:
        model=UserProfile
        fields=['username','name',]


class OutboxGroupReceiverSerializer(serializers.ModelSerializer):
    receiver = ReceiverSerializer()
    read_time = serializers.DateTimeField(read_only=True, format='%Y-%m-%d %H:%M')
    class Meta:
        model=GroupReceiverMessage
        fields=['receiver','read_time',]


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model=Group
        fields=['group_type','group_name','group_id']


class OutboxGroupSerializer(serializers.ModelSerializer):
    group_receiver_message=OutboxGroupReceiverSerializer(many=True)
    group=GroupSerializer()
    class Meta:
        model=ReceiverGroup
        fields=['group_receiver_message','group']


class OutboxReceiverMessageSerializer(serializers.ModelSerializer):
    receiver=ReceiverSerializer()
    read_time=serializers.DateTimeField(read_only=True,format='%Y-%m-%d %H:%M')
    class Meta:
        model=ReceiverMessage
        fields=['read_time','receiver',]


class MessageFileSerializer(serializers.ModelSerializer):
    class Meta:
        model=MessageFile
        fields=['file_name','file']


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
        fields=['receiver_message','receiver_group','title','body','send_time','if_delete','if_collect','message_file']


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
    sender=serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    reply_message_id=serializers.IntegerField(required=False,help_text='回复的父消息')
    def create(self, validated_data):
        title='未命名'
        # body=''
        sender=validated_data.get('sender')
        send_state=0
        reply_message_id=validated_data.get('reply_message_id')
        if reply_message_id:
            message=Message.objects.filter(Q(id=reply_message_id,receiver_message__receiver_id=sender)|Q(id=reply_message_id,receiver_group__group_receiver_message__receiver=sender))
            if message:
                obj = Message.objects.create(title=title, sender_id=sender, send_state=send_state,reply_message_id=reply_message_id)
                return obj
            else:
                raise serializers.ValidationError('你并未接收到该消息，没有权限回复该消息！')
        else:
            obj = Message.objects.create(title=title, sender_id=sender, send_state=send_state)
            return obj
    class Meta:
        model=Message
        fields=['id','sender','reply_message_id','title','body','send_state','type']


#改件
class OutboxMessageUpdateSerializer(serializers.ModelSerializer):
    id=serializers.IntegerField(read_only=True)
    sender=serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    title=serializers.CharField(required=True,help_text='标题')
    body=serializers.CharField(required=True,help_text='内容')
    # type=serializers.IntegerField(required=True,help_text='类型')
    # send_state=serializers.IntegerField(required=True,help_text='发送状态')
    reply_message_id=serializers.IntegerField(required=False,help_text='父消息id')
    def update(self, instance, validated_data):
        # instance.title = validated_data.get('title', instance.title)
        # instance.body = validated_data.get('body', instance.body)
        # send_state=instance.send_state
        # if send_state==1:
        #     pass
        # elif send_state==0:
        #     instance.send_state = validated_data.get('send_state', instance.send_state)
        # instance.type=validated_data.get('type',instance.type)
        # a=validated_data.get('reply_message_id', instance.reply_message_id)
        # if a:
        #     instance.reply_message_id=a
        # instance.update_time=datetime.now()
        # instance.save()
        # return instance
        if instance.send_state==0:
            instance.title = validated_data.get('title', instance.title)
            instance.body = validated_data.get('body', instance.body)
            instance.send_state = validated_data.get('send_state', instance.send_state)
            instance.type = validated_data.get('type', instance.type)
            instance.reply_message_id = validated_data.get('reply_message_id', instance.reply_message_id)
            instance.send_time = datetime.now()
            instance.save()
            return instance
        else:
            raise serializers.ValidationError('已发送信息不能修改！')
    class Meta:
        model=Message
        fields=['title','body','sender','id','type','send_state','reply_message_id','update_time','send_time']


#上传文件
class OutboxMessageFileCreateSerializer(serializers.Serializer):
    id=serializers.IntegerField(read_only=True,help_text='文件id')
    message_id=serializers.IntegerField(required=True,help_text='消息id')
    file_name=serializers.CharField(required=True,help_text='文件名')
    file=serializers.FileField(required=True,help_text='文件')
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    def create(self, validated_data):
        mess_id = validated_data.get('message_id')
        message = Message.objects.filter(id=mess_id)
        if message:
            u = validated_data.get('user')
            if message[0].sender_id==u:
                mes_file=MessageFile(message_id=validated_data.get('message_id'),file_name=validated_data.get('file_name'),file=validated_data.get('file'))
                mes_file.save()
                return mes_file
            else:
                raise serializers.ValidationError("当前用户不是发件人，没有权限上传文件！")
        else:
            raise serializers.ValidationError('消息不存在！')
    class Meta:
        model=MessageFile
        fields=['message_id','file_name','file','id','user']


#更改上传文件
class OutboxMessageFileUpdateSerializer(serializers.Serializer):
    file_name=serializers.CharField(help_text='文件名')
    file=serializers.FileField(help_text='文件')
    def update(self, instance, validated_data):
        instance.file_name=validated_data.get('file_name',instance.file_name)
        instance.file=validated_data.get('file',instance.file)
        instance.save()
        return instance
    class Meta:
        model=MessageFile
        fields=['message_id','file_name','file','id','user']


#创建接受者
class OutboxMessageReceiverCreateSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    message_id=serializers.IntegerField(required=True,help_text='消息id')
    receiver_id=serializers.IntegerField(required=True,help_text='接收用户id')
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    def create(self, validated_data):
        mess_id=validated_data.get('message_id')
        message=Message.objects.filter(id=mess_id)
        if message:
            u = validated_data.get('user')
            if message[0].sender_id==u:
                receiver_id=validated_data.get('receiver_id')
                rece=UserProfile.objects.filter(id=receiver_id)
                if rece:
                    mes_receiver = ReceiverMessage(message_id=validated_data.get('message_id'),receiver_id=receiver_id)
                    try:
                        mes_receiver.save()
                    except:
                        raise serializers.ValidationError('已向该用户发送消息，勿重复发送！')
                    contact=RecentContact.objects.filter(user_id=u,contact_id=receiver_id)
                    if contact:
                        contact[0].add_time=datetime.now
                    else:
                        RecentContact.objects.create(user_id=u,contact_id=receiver_id)
                    return mes_receiver
                else:
                    raise serializers.ValidationError("接收用户不存在！")
            else:
                raise serializers.ValidationError("当前用户不是发件人，没有权限发送该消息给他人！")
        else:
            raise serializers.ValidationError('消息不存在！')
    class Meta:
        model=ReceiverMessage
        fields=['message_id','receiver_id','user','id']



# 接收组创建
class OutboxGroupCreateSerializer(serializers.ModelSerializer):
    # id=serializers.IntegerField(read_only=True)
    message_id=serializers.IntegerField(required=True,help_text='消息id')
    # group_name=serializers.CharField(read_only=True,help_text='组织名称')
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    gro_id=serializers.CharField(required=True,help_text='组织的id')
    def create(self, validated_data):
        message_id=validated_data.get('message_id')
        # group_type=validated_data.get('group_type')
        # group_id=validated_data.get('group_id')
        # group_name=validated_data.get('group_name')
        user=validated_data.get('user')
        mess=Message.objects.filter(id=message_id)
        if mess:
            if mess[0].sender_id==user:
                gro_id=validated_data.get('gro_id')
                group=Group.objects.filter(id=gro_id)
                if group:
                    ad=GroupAdministrator.objects.filter(admin=user,group_id=gro_id)
                    if ad:
                        group_rece=ReceiverGroup.objects.create(group=group[0],message=mess[0])
                        if group[0].group_type==1:
                            group_receivers = UserProfile.objects.filter(student__score__schedule_lesson_id=group[0].id)
                            for i in group_receivers:
                                GroupReceiverMessage.objects.create(receiver_group=group_rece,receiver=i)
                        elif group[0].group_type==2:
                            group_receivers=UserProfile.objects.filter(student__cla_id=group[0].id)
                            for i in group_receivers:
                                GroupReceiverMessage.objects.create(receiver_group=group_rece,receiver=i)
                        elif group[0].group_type==3:
                            group_receivers=UserProfile.objects.filter(student__cla__colloge_id=group[0].id)
                            for i in group_receivers:
                                GroupReceiverMessage.objects.create(receiver_group=group_rece,receiver=i)
                        elif group[0].group_type==4:
                            group_receivers=UserProfile.objects.filter(student__cla__major_id=group[0].id)
                            for i in group_receivers:
                                GroupReceiverMessage.objects.create(receiver_group=group_rece,receiver=i)
                        # elif group[0].group_type==5:
                        #     pass
                        else:
                            raise serializers.ValidationError('找不到组织类型！')
                        return group_rece
                    else:
                        if group[0].group_type==5:
                            def_g=DefGroup.objects.filter(def_group_member=user,id=gro_id)
                            if def_g:
                                group_rece=ReceiverGroup.objects.create(group=def_g[0],message=mess[0])
                                group_receivers=UserProfile.objects.filter(def_group_member__def_group=def_g[0])
                                for i in group_receivers:
                                    if i.id!=user:
                                        GroupReceiverMessage.objects.create(receiver_group=group_rece,receiver=i)
                                return group_rece
                            else:
                                raise serializers.ValidationError('自定义组织不存在！')
                                # group_receivers=UserProfile.objects.filter()
                        else:
                            raise serializers.ValidationError('你不是该组织管理员，没有权限群发消息！')
                else:
                    raise serializers.ValidationError('组织不存在！')
            else:
                raise serializers.ValidationError('你不是该消息发送者，没有权限发送当前消息！')
        else:
            raise serializers.ValidationError('消息不存在！')
    class Meta:
        model=ReceiverGroup
        fields=['message_id','user','gro_id']

#收件箱
#已读、收藏、删除
class InboxMessageReceiverUpdateSerializer(serializers.Serializer):
    id=serializers.IntegerField(read_only=True)
    if_read=serializers.BooleanField(required=False,help_text='标记是否已读')
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
    if_read=serializers.BooleanField(required=False,help_text='标记是否已读')
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