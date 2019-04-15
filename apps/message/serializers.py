#-*- coding:utf-8 -*-

from rest_framework import serializers
from .models import Message,ReceiverMessage,MessageFile,ReceiverGroup,GroupReceiverMessage
from rest_framework_recursive.fields import RecursiveField
# from users.serializer import UserProfileSerializer
from users.models import UserProfile,Class,Colloge,Major
from lessons.models import ScheduleLesson,Lesson
from datetime import datetime

#发件箱
class ReceiverSerializer(serializers.ModelSerializer):
    class Meta:
        model=UserProfile
        fields=['username','name',]


class OutboxGroupReceiverSerializer(serializers.ModelSerializer):
    receiver = ReceiverSerializer()
    class Meta:
        model=GroupReceiverMessage
        fields=['receiver','read_time',]


class OutboxGroupSerializer(serializers.ModelSerializer):
    group_receiver_message=OutboxGroupReceiverSerializer(many=True)
    class Meta:
        model=ReceiverGroup
        fields=['group_receiver_message','group_type','group_id','group_name']


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
        fields=['receiver_message','receiver_group','title','body','send_time','if_delete','if_collect','message_file','reply_message']


#发件 初始化空邮件
class OutboxMessageCreateSerializer(serializers.ModelSerializer):
    id=serializers.IntegerField(read_only=True)
    sender=serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    reply_message=serializers.IntegerField(required=False,help_text='回复的父消息')
    def create(self, validated_data):
        title='未命名'
        # body=''
        sender=validated_data.get('sender')
        send_state=0
        reply_message=validated_data.get('reply_message')
        obj=Message.objects.create(title=title,sender=sender,send_state=send_state,reply_message=reply_message)
        return obj
    class Meta:
        model=Message
        fields=['id','sender','reply_message']


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
    reply_message_id=serializers.IntegerField(required=False)
    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        instance.body = validated_data.get('body', instance.body)
        instance.send_state = validated_data.get('send_state', instance.send_state)
        instance.type=validated_data.get('type',instance.type)
        a=validated_data.get('reply_message_id', instance.reply_message_id)
        if a:
            instance.reply_message_id=a
        instance.send_time=datetime.now()
        instance.save()
        return instance
    class Meta:
        model=Message
        fields=['title','body','sender','id','type','send_state','reply_message_id']


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
                try:
                    mes_receiver = ReceiverMessage(message_id=validated_data.get('message_id'),receiver_id=validated_data.get('receiver_id'))
                    mes_receiver.save()
                    return mes_receiver
                except:
                    raise serializers.ValidationError("接收用户不存在！")
            else:
                raise serializers.ValidationError("当前用户不是发件人，没有权限上传文件！")
        else:
            raise serializers.ValidationError('消息不存在！')
    class Meta:
        model=ReceiverMessage
        fields=['message_id','receiver_id','user','id']



# 接收组创建
class OutboxGroupCreateSerializer(serializers.ModelSerializer):
    # id=serializers.IntegerField(read_only=True)
    message_id=serializers.IntegerField(required=True,help_text='消息id')
    group_name=serializers.CharField(read_only=True,help_text='组织名称')
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    def create(self, validated_data):
        message_id=validated_data.get('message_id')
        group_type=validated_data.get('group_type')
        group_id=validated_data.get('group_id')
        # group_name=validated_data.get('group_name')
        user=validated_data.get('user')
        mess=Message.objects.filter(id=message_id)
        if mess:
            if mess[0].sender_id==user:
                if group_type == 1:
                    sch_les = ScheduleLesson.objects.filter(id=group_id)
                    if sch_les:
                        group_receivers = UserProfile.objects.filter(student__score__schedule_lesson=sch_les[0])
                        group_name = sch_les[0].class_name
                        if group_receivers:
                            group = ReceiverGroup.objects.create(group_id=group_id, group_type=group_type,
                                                                 group_name=group_name, message=mess[0])
                            # id = validated_data.get('id')
                            for g_r in group_receivers:
                                group_receiver = GroupReceiverMessage(receiver_group=group, receiver=g_r)
                                group_receiver.save()
                            return group
                    else:
                        raise serializers.ValidationError('课程表课程id不存在！')
                elif group_type == 2:
                    cla = Class.objects.filter(id=group_id)
                    if cla:
                        group_name = cla[0].name
                        group_receivers = UserProfile.objects.filter(student__cla__id=cla[0])
                        if group_receivers:
                            group = ReceiverGroup.objects.create(group_id=group_id, group_type=group_type,
                                                                 group_name=group_name, message=mess[0])
                            for g_r in group_receivers:
                                group_receiver = GroupReceiverMessage(receiver_group=group, receiver=g_r)
                                group_receiver.save()
                            return group
                    else:
                        raise serializers.ValidationError('班级id不存在！')
                elif group_type == 3:
                    colloge = Colloge.objects.filter(id=group_id)
                    if colloge:
                        group_name = colloge[0].name
                        group_receivers = UserProfile.objects.filter(student__cla__colloge=colloge[0])
                        if group_receivers:
                            group = ReceiverGroup.objects.create(group_id=group_id, group_type=group_type,
                                                                 group_name=group_name, message=mess[0])
                            for g_r in group_receivers:
                                group_receiver = GroupReceiverMessage(receiver_group=group, receiver=g_r)
                                group_receiver.save()
                            return group
                    else:
                        raise serializers.ValidationError('学院id不存在！')
                else:
                    maj = Major.objects.filter(id=group_id)
                    if maj:
                        group_name = maj[0].name
                        group_receivers = UserProfile.objects.filter(student__cla__major=maj[0])
                        if group_receivers:
                            group = ReceiverGroup.objects.create(group_id=group_id, group_type=group_type,
                                                                 group_name=group_name, message=mess[0])
                            for g_r in group_receivers:
                                group_receiver = GroupReceiverMessage(receiver_group=group, receiver=g_r)
                                group_receiver.save()
                            return group
                    else:
                        raise serializers.ValidationError('专业id不存在！')
            else:
                raise serializers.ValidationError('你没有权力发送当前消息！')
        else:
            raise serializers.ValidationError('消息不存在！')
    class Meta:
        model=ReceiverGroup
        fields=['message_id','group_id','group_type','group_name','user']

#收件箱
#已读、收藏、删除
class OutboxMessageReceiverUpdateSerializer(serializers.Serializer):
    # id=serializers.IntegerField(read_only=True)
    if_read=serializers.BooleanField(required=False,help_text='标记是否已读')
    if_delete=serializers.BooleanField(required=False,help_text='是否回收')
    if_collect=serializers.BooleanField(required=False,help_text='是否收藏')
    # read_time = serializers.HiddenField()
    # user = serializers.HiddenField(
    #     default=serializers.CurrentUserDefault()
    # )
    def update(self, instance, validated_data):
        instance.if_delete=validated_data.get('if_delete',instance.if_delete)
        instance.if_collect=validated_data.get('if_collect',instance.if_collect)
        if validated_data.get('if_read'):
            # ReceiverMessage
            if instance.read_time:
                pass
            else:
                instance.read_time=datetime.now()
        # instance.send_time = datetime.now()
        instance.save()
        return instance
    class Meta:
        model=ReceiverMessage
        fields=['id','read_time','if_delete','if_collect','if_read']








