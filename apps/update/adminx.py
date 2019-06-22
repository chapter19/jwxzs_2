#-*- coding:utf-8 -*-

import xadmin

from .models import UpdateLog

class UpdateLogAdmin(object):
    list_display=['desc','verbose_id','url','task_id','class_and_method','start_time','type','stop_time','status','user','id']
    search_fields=['desc','id','verbose_id','task_id','user__username','user__name','class_and_method']
    list_filter=['desc','verbose_id','task_id','class_and_method','start_time','type','stop_time','status','user__username']
    refresh_times = [3, 5, 10, 30, 60, 120]
    model_icon = 'fa fa-clock-o'

xadmin.site.register(UpdateLog,UpdateLogAdmin)