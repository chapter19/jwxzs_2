#-*- coding:utf-8 -*-

import xadmin
from xadmin import views
from .models import Message,ReceiverMessage,MessageFile,ReceiverGroup,GroupReceiverMessage
from users.models import Colloge,Class,Major,UserProfile
from lessons.models import ScheduleLesson
from django import forms
from ckeditor_uploader.widgets import CKEditorUploadingWidget

class ReceiverMessageInline(object):
    model=ReceiverMessage
    extra=0


class MessageFileInline(object):
    model=MessageFile
    extra=0


class MessageAdmin(object):
    list_display=['title','sender','type','body','send_time','reply_message','send_state','id']
    search_fields=['title','sender__username','sender__studentdetail__base_data__name','body','reply_message__title','reply_message__body','reply_message__sender__username','reply_message__sender__studentdetail__base_data__name']
    list_filter=['type','sender__name','send_time','send_state','reply_message__title']
    inlines=[ReceiverMessageInline,MessageFileInline]
    model_icon='fa fa-bell-o'
    # relfield_style = 'fk_ajax'

# class ReceiverClassAdmin(object):
#     list_display=['message','cla','add_time']

class ReceiverGroupAdmin(object):
    list_display=['group_name','group_id','group_type','id']
    search_fields=['group_name','group_id','message__title','id','group_receiver_message__receiver__name','group_receiver_message__receiver__username']
    list_filter=['group_type','message__title','group_name','group_receiver_message__receiver__name','group_receiver_message__receiver__username']
    model_icon = 'fa fa-bullhorn'
    def save_models(self):
        obj=self.new_obj
        obj.save()
        # print(obj)
        group_type=obj.group_type
        group_id=obj.group_id
        # group_name=obj.group_name
        message=obj.message

        if group_type == 1:
            sch_les = ScheduleLesson.objects.filter(id=group_id)
            if sch_les:
                group_receivers = UserProfile.objects.filter(student__score__schedule_lesson=sch_les[0])
                group_name = sch_les[0].lesson.name + ' ' + sch_les[0].class_name
                if group_receivers:
                    group = obj
                    if group.group_name:
                        pass
                    else:
                        group.group_name = group_name
                        group.save()
                    for g_r in group_receivers:
                        group_receiver = GroupReceiverMessage(receiver_group=group, receiver=g_r)
                        group_receiver.save()
        elif group_type == 2:
            cla = Class.objects.filter(id=group_id)
            if cla:
                group_name = cla[0].name
                group_receivers = UserProfile.objects.filter(student__cla=cla[0])
                if group_receivers:
                    group = obj
                    if group.group_name:
                        pass
                    else:
                        group.group_name=group_name
                        group.save()
                    for g_r in group_receivers:
                        group_receiver = GroupReceiverMessage(receiver_group=group, receiver=g_r)
                        group_receiver.save()
        elif group_type == 3:
            colloge = Colloge.objects.filter(id=group_id)
            if colloge:
                group_name = colloge[0].name
                group_receivers = UserProfile.objects.filter(student__cla__colloge=colloge[0])
                if group_receivers:
                    group = obj
                    if group.group_name:
                        pass
                    else:
                        group.group_name = group_name
                        group.save()
                    for g_r in group_receivers:
                        group_receiver = GroupReceiverMessage(receiver_group=group, receiver=g_r)
                        group_receiver.save()
        else:
            maj = Major.objects.filter(id=group_id)
            if maj:
                group_name = str(maj[0].grade)+'级'+maj[0].name
                group_receivers = UserProfile.objects.filter(student__cla__major=maj[0])
                if group_receivers:
                    group = obj
                    if group.group_name:
                        pass
                    else:
                        group.group_name = group_name
                        group.save()
                    for g_r in group_receivers:
                        group_receiver = GroupReceiverMessage(receiver_group=group, receiver=g_r)
                        group_receiver.save()


class GroupReceiverMessageAdmin(object):
    list_display=['receiver','receiver_group','read_time','if_delete','if_collect','if_report','id']
    search_fields =['receiver__username','receiver__name','receiver_group__id','receiver_group__group_name','receiver_group__group_id','receiver_group__message__title','receiver_group__message__id']
    list_filter=['read_time','if_delete','if_collect','receiver__name','receiver_group__group_name','receiver_group__group_id','receiver_group__group_type','receiver_group__message__title','receiver_group__message__id','receiver_group__message__type','receiver_group__message__send_time','receiver_group__message__send_state']
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