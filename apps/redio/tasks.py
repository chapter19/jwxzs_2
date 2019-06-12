#-*- coding:utf-8 -*-

from celery import shared_task
from logs.models import Log
from utils.address import get_address
from .models import Redio
from utils.settings import MY_WORD,MY_USERNAME

from spiders.redio import SpiderRedio

@shared_task
def get_redio():
    spider=SpiderRedio(id=MY_USERNAME,password=MY_WORD)
    spider.sign_in()
    spider.get_redio_GongGao()
    spider.get_redio_TongZhi()




@shared_task
def redio_retrieve_log(ip,user_id,id):
    redio=Redio.objects.get(id=id)
    message='查看了教务通知" %s "的详情'% redio.title
    Log.objects.create(ip=ip,user_id=user_id,action_type='match',address=get_address(ip),message=message)


@shared_task
def redio_list_log(ip,user_id,title,time_min,time_max):
    if title:
        if time_min and time_max:
            message='搜索了标题可能为" %s "且发布时间在" %s-%s "之间的教务通知'%(title,time_min,time_max)
        elif time_max:
            message='搜索了标题可能为" %s "且发布时间在" %s "之前的教务通知'%(title,time_max)
        elif time_min:
            message='搜索了标题可能为" %s "且发布时间在" %s "之后的教务通知'%(title,time_min)
        else:
            message='搜索了标题可能为" %s "的教务通知'%(title)
        Log.objects.create(ip=ip,address=get_address(ip),user_id=user_id,action_type='match',message=message)
