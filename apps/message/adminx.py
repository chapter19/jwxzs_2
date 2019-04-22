#-*- coding:utf-8 -*-

import xadmin
from xadmin import views

from .models import Message,ReceiverMessage,MessageFile,ReceiverGroup,GroupReceiverMessage
from users.models import Colloge,Class,Major,UserProfile
from lessons.models import ScheduleLesson
from groups.models import DefGroup,DefGroupMember

class ReceiverMessageInline(object):
    model=ReceiverMessage
    extra=0


class MessageFileInline(object):
    model=MessageFile
    extra=0

class ReceiverGroupInline(object):
    model=ReceiverGroup
    extra=0


class MessageAdmin(object):
    list_display=['title','sender','type','body','send_time','reply_message','send_state','id']
    search_fields=['title','sender__username','sender__name','body','reply_message__title','reply_message__body','reply_message__sender__username','reply_message__sender__name']
    list_filter=['type','sender__name','send_time','send_state','reply_message__title']
    inlines=[ReceiverMessageInline,MessageFileInline,]
    model_icon='fa fa-bell-o'
    # relfield_style = 'fk_ajax'

# class ReceiverClassAdmin(object):
#     list_display=['message','cla','add_time']

class ReceiverGroupAdmin(object):
    list_display=['group','id']
    search_fields=['group__group_name','group__group_id','message__title','id','group_receiver_message__receiver__name','group_receiver_message__receiver__username']
    list_filter=['group__group_type','message__title','group__group_name','group_receiver_message__receiver__name','group_receiver_message__receiver__username']
    model_icon = 'fa fa-bullhorn'
    def save_models(self):
        obj=self.new_obj
        obj.save()
        # print(obj)
        # group_type=obj.group_type
        # group_id=obj.group_id
        # group_name=obj.group_name
        message=obj.message
        group=obj.group
        if group.group_type == 1:
            sch_les = ScheduleLesson.objects.filter(id=group.group_id)
            if sch_les:
                group_receivers = UserProfile.objects.filter(student__score__schedule_lesson=sch_les[0])
                if group_receivers:
                    for g_r in group_receivers:
                        group_receiver = GroupReceiverMessage(receiver_group=obj, receiver=g_r)
                        group_receiver.save()
        elif group.group_type == 2:
            cla = Class.objects.filter(id=group.group_id)
            if cla:
                group_receivers = UserProfile.objects.filter(student__cla=cla[0])
                if group_receivers:
                    for g_r in group_receivers:
                        group_receiver = GroupReceiverMessage(receiver_group=obj, receiver=g_r)
                        group_receiver.save()
        elif group.group_type == 3:
            colloge = Colloge.objects.filter(id=group.group_id)
            if colloge:
                group_receivers = UserProfile.objects.filter(student__cla__colloge=colloge[0])
                if group_receivers:
                    for g_r in group_receivers:
                        group_receiver = GroupReceiverMessage(receiver_group=obj, receiver=g_r)
                        group_receiver.save()
        elif group.group_type==4:
            maj = Major.objects.filter(id=group.group_id)
            if maj:
                group_receivers = UserProfile.objects.filter(student__cla__major=maj[0])
                if group_receivers:
                    for g_r in group_receivers:
                        group_receiver = GroupReceiverMessage(receiver_group=obj, receiver=g_r)
                        group_receiver.save()
        elif group.group_type==5:
            def_group=DefGroup.objects.filter(id=group.group_id)
            if def_group:
                group_receivers=UserProfile.objects.filter(def_group_member__def_group=def_group[0])
                if group_receivers:
                    for g_r in group_receivers:
                        if g_r!=message.sender:
                            group_receiver=GroupReceiverMessage(receiver_group=obj,receiver=g_r)
                            group_receiver.save()


class GroupReceiverMessageAdmin(object):
    list_display=['receiver','receiver_group','read_time','if_delete','if_collect','if_report','id']
    search_fields =['receiver__username','receiver__name','receiver_group__id','receiver_group__group__group_name','receiver_group__group__group_id','receiver_group__message__title','receiver_group__message__id']
    list_filter=['read_time','if_delete','if_collect','receiver__name','receiver_group__group__group_name','receiver_group__group__group_id','receiver_group__group__group_type','receiver_group__message__title','receiver_group__message__id','receiver_group__message__type','receiver_group__message__send_time','receiver_group__message__send_state']
    list_editable=['if_delete','if_collect','if_report']
    model_icon = 'fa fa-comments-o'


class ReceiverMessageAdmin(object):
    list_display=['message','receiver','read_time','if_delete','if_collect','if_report','id','get_sender']
    search_fields=['message__title','message__body','message__sender__username','receiver__username']
    list_filter=['read_time','if_delete','if_collect']
    list_editable = ['if_delete', 'if_collect', 'if_report']
    model_icon = 'fa fa-comment-o'
    # relfield_style = 'fk_ajax'


class MessageFileAdmin(object):
    list_display=['message','file_name','file','id','get_sender']
    search_fields=['file_name','message__title','message__body','message__sender__username','message__sender__name','message__receiver_message__receiver__username','message__receiver_message__receiver__name']
    list_filter=['message__title','file_name','message__body','message__type','message__send_time','message__send_state','message__reply_message__type','message__reply_message__send_time']
    model_icon = 'fa fa-file'




xadmin.site.register(Message,MessageAdmin)
# xadmin.site.register(ReceiverClass,ReceiverClassAdmin)
xadmin.site.register(ReceiverMessage,ReceiverMessageAdmin)
xadmin.site.register(MessageFile,MessageFileAdmin)
xadmin.site.register(ReceiverGroup,ReceiverGroupAdmin)
xadmin.site.register(GroupReceiverMessage,GroupReceiverMessageAdmin)