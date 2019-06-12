#-*- coding:utf-8 -*-

import xadmin

from .models import TheCheck,CheckedStudent


class TheCheckAdmin(object):
    list_display=['schedule_lesson','promoter','start_time','time_limit','password','id','check_status']
    search_fields=['promoter__name','promoter__username','schedule_lesson__class_name','schedule_lesson__lesson__name','password']
    list_filter=['check_status','start_time','time_limit','password']


class CheckedStudentAdmin(object):
    list_display=['student','the_check','check_time','id']
    search_fields=['student__name','student__username','the_check__schedule_lesson__class_name','the_check__schedule_lesson__lesson__name','the_check__password']
    list_filter=['student__name','student__username','student__gender','check_time','the_check__check_status','the_check__start_time','the_check__time_limit','the_check__password']


xadmin.site.register(TheCheck,TheCheckAdmin)
xadmin.site.register(CheckedStudent,CheckedStudentAdmin)