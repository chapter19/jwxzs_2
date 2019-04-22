#-*- coding:utf-8 -*-

import xadmin
from .models import Group,GroupAdministrator,DefGroup,DefGroupMember

class GroupAdmin(object):
    list_display=['group_name','group_type','group_id','add_time','id']
    search_fields=['group_name','group_id']
    list_filter=['group_name','group_type','add_time','group_id']
    model_icon = 'fa fa-users'


class GroupAdministratorAdmin(object):
    list_display=['admin','group','add_time','if_super','id']
    search_fields=['admin__username','admin__name','group__group_name','group__group_id']
    list_filter=['group__group_name','admin__username','admin__gender','admin__is_teacher','admin__name','group__group_id']
    model_icon = 'fa fa-user'

class DefGroupAdmin(object):
    list_display=['name','creater','add_time','id']
    search_fields=['name','creater__username','creater__name']
    list_filter=['name','creater__username','creater__name','creater__gender','creater__is_teacher']
    model_icon = 'fa fa-user'


class DefGroupMemberAdmin(object):
    list_display=['member','def_group','add_time','id']
    search_fields=['member__name','member__username','def_group__name','def_group__creater__name','def_group__creater__username']
    list_filter=['member__name','member__username','member__is_student','def_group__name','def_group__creater__name','def_group__creater__username','def_group__creater__is_teacher']
    model_icon = 'fa fa-user'




xadmin.site.register(Group,GroupAdmin)
xadmin.site.register(GroupAdministrator,GroupAdministratorAdmin)
xadmin.site.register(DefGroup,DefGroupAdmin)
xadmin.site.register(DefGroupMember,DefGroupMemberAdmin)