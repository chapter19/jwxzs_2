#-*- coding:utf-8 -*-
import xadmin
from .models import Redio

class RedioAdmin(object):
    list_display=['title','id','body','time','add_time']
    list_filter=['add_time','title','body','time']
    search_fields=['title','body','id']
    model_icon = 'fa fa-bullhorn'


xadmin.site.register(Redio,RedioAdmin)