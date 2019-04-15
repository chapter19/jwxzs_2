#-*- coding:utf-8 -*-

import xadmin
from xadmin import views
from .models import Message,ReceiverMessage,MessageFile,ReceiverGroup
from django import forms
from ckeditor_uploader.widgets import CKEditorUploadingWidget



class MessageAdmin(object):
    list_display=['title','sender','type','body','send_time','reply_message','send_state','id']
    search_fields=['title','sender__username','sender__studentdetail__base_data__name','body','reply_message__title','reply_message__body','reply_message__sender__username','reply_message__sender__studentdetail__base_data__name']
    list_filter=['type','sender__name','send_time','report_time','send_state','reply_message__title']


# class ReceiverClassAdmin(object):
#     list_display=['message','cla','add_time']

class ReceiverGroupAdmin(object):
    list_display=['group_name','group_id','group_type']


class ReceiverMessageAdmin(object):
    list_display=['message','receiver','read_time','if_delete','if_collect','id']
    search_fields=['message__title','message__body','message__sender__username','message__sender__studentdetail__base_data__name','receiver__username','receiver__studentdetail__base_data__name']
    list_filter=['read_time','if_delete','if_collect']


class MessageFileAdmin(object):
    list_display=['message','file_name','file','id']
    search_fields=['file_name','message__title','message__body','message__sender__username','message__sender__studentdetail__base_data__name','message__receive_message__receiver__username','message__receive_message__receiver__studentdetail__base_data__name']
    list_filter=['message__title','file_name','message__body','message__type','message__send_time','message__send_state','message__report_time','message__reply_message__type','message__send_time','message__report_time']





xadmin.site.register(Message,MessageAdmin)
# xadmin.site.register(ReceiverClass,ReceiverClassAdmin)
xadmin.site.register(ReceiverMessage,ReceiverMessageAdmin)
xadmin.site.register(MessageFile,MessageFileAdmin)
xadmin.site.register(ReceiverGroup,ReceiverGroupAdmin)