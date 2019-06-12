#-*- coding:utf-8 -*-
import xadmin
from .models import CollectFriends,RecentContact



class CollectFriendsAdmin(object):
    list_display=['friend','user','add_time','id']
    search_fields=['friend__name','friend__username','user__name','user__username']
    list_filter=['friend__name','friend__username','user__name','user__username','friend__gender','user__gender','friend__is_student','friend__is_teacher','user__is_student','user__is_teacher']
    model_icon = 'fa fa-users'

class RecentContactAdmin(object):
    list_display=['contact','user','add_time','id']
    search_fields=['contact__name','contact__username','user__name','user__username']
    list_filter=['contact__name','contact__username','user__name','user__username','contact__gender','user__gender','contact__is_student','contact__is_teacher','user__is_student','user__is_teacher']
    model_icon = 'fa fa-users'


xadmin.site.register(CollectFriends,CollectFriendsAdmin)
xadmin.site.register(RecentContact,RecentContactAdmin)