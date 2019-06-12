#-*- coding:utf-8 -*-
import os,django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "jwxzs_2.settings")# project_name 项目名称
django.setup()
import time

from message.models import Message,ReceiverMessage

def create_message(message_count=20):
    for i in range(message_count):
        mess='注意控制进度'+str(i)
        body='<p>{0}</p>'.format(mess)
        if i%2==1:
            ty=2
        else:
            ty=3
        message=Message.objects.create(sender_id=62609,title=mess,body=body,type=ty)
        ReceiverMessage.objects.create(message=message,receiver_id=3)
        ReceiverMessage.objects.create(message=message,receiver_id=2)
        if i%2==1:
            pass
        else:
            reply_mess1=Message.objects.create(reply_message=message,title='回复：'+mess,body='<p>好好，我知道了</p>',sender_id=3,type=5)
            ReceiverMessage.objects.create(message=reply_mess1, receiver_id=62609)
            reply_mess2=Message.objects.create(reply_message=message,title='回复：'+mess,body='<p>行，我知道了</p>',sender_id=2)
            ReceiverMessage.objects.create(message=reply_mess2, receiver_id=62609)
        time.sleep(3)
        print(mess)

def create_message2(message_count=20):
    for i in range(message_count):
        mess='下午两点半去做汇报'+str(i)
        body='<p>{0}</p>'.format(mess)
        message=Message.objects.create(sender_id=2,title=mess,body=body,type=3)
        ReceiverMessage.objects.create(message=message,receiver_id=4)
        if i%3==1:
            reply_mess=Message.objects.create(reply_message=message,title='回复：'+mess,body='<p>知道了知道了别吵了</p>',sender_id=4)
            ReceiverMessage.objects.create(message=reply_mess,receiver_id=2)
        time.sleep(2)
        print(mess)

def create_message3(message_count=20):
    for i in range(message_count):
        mess='抓紧时间'+str(i)
        body='<p>{0}</p>'.format(mess)
        message=Message.objects.create(sender_id=2,title=mess,body=body,type=3)
        ReceiverMessage.objects.create(message=message,receiver_id=3)
        if i%3==1:
            reply_mess=Message.objects.create(reply_message=message,title='回复：'+mess,body='<p>好</p>',sender_id=3)
            ReceiverMessage.objects.create(message=reply_mess,receiver_id=2)
        time.sleep(2)
        print(mess)

def create_message4(message_count=20):
    for i in range(message_count):
        mess='周三给你看进度'+str(i)
        body='<p>{0}</p>'.format(mess)
        message=Message.objects.create(sender_id=3,title=mess,body=body,type=3)
        ReceiverMessage.objects.create(message=message,receiver_id=2)
        if i%2==1:
            reply_mess=Message.objects.create(reply_message=message,title='回复：'+mess,body='<p>好</p>',sender_id=2)
            ReceiverMessage.objects.create(message=reply_mess,receiver_id=3)
        time.sleep(2)
        print(mess)

if __name__ == '__main__':
    # create_message()
    create_message4()