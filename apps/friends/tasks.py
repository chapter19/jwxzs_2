#-*- coding:utf-8 -*-

from celery import shared_task
from logs.models import Log
from utils.address import get_address
from message.models import Message,ReceiverMessage

from .models import UserProfile

@shared_task
def collect_friend_log(ip,user_id,friend_id):
    if friend_id:
        friend=UserProfile.objects.get(id=friend_id)
        message='关注了好友" %s "'%friend.name
        Log.objects.create(ip=ip,user_id=user_id,address=get_address(ip),action_type='create',message=message)


@shared_task
def send_collect_message(user_id,friend_id):
    user = UserProfile.objects.get(id=user_id)
    title = '关注了你'.format(user.name)
    body = '我是{0}，我刚关注了你，为了方便联系快来关注我吧~'.format(user.name)
    message = Message.objects.create(title=title, body=body, sender=user, type=3)
    ReceiverMessage.objects.create(message=message, receiver_id=friend_id)

