#-*- coding:utf-8 -*-

import xadmin

from .models import Log,Ip

class LogAdmin(object):
    model_icon = 'fa fa-clock-o'
    list_display=['message','user','action_type','action_time','ip','address','id']

class IpAdmin(object):
    model_icon = 'fa fa-clock-o'
    list_display=['ip','address','adcode','rectangle']

xadmin.site.register(Log,LogAdmin)
xadmin.site.register(Ip,IpAdmin)