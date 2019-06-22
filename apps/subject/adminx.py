#-*- coding:utf-8 -*-
import xadmin
from .models import PingJiaoTeacher,LessonLabels,StepOneLessonTeacher,MyXuanKe

class PingJiaoTeacherAdmin(object):
    model_icon = 'fa fa-book'
    list_display=['student','teacher','lesson_name','semester','code','grade','score','semester']
    search_fields=['student__name','student__id','teacher__name','teacher__id']
    list_filter=['student__name','student__gender','student__cla__grade','teacher__name','teacher__gender','semester','score','grade']

class LessonLabelsAdmin(object):
    model_icon = 'fa fa-book'
    list_display=['lesson','label','add_time']
    search_fields=['lesson__name','label','lesson__id']
    list_filter=['lesson__name','label']

class StepOneLessonTeacherAdmin(object):
    model_icon = 'fa fa-book'
    list_display=['lesson','teacher','semester','post_code','add_time',]
    search_fields=['lesson__name','lesson__id','teacher__name','teacher__id']
    list_filter=['lesson__name','teacher__name','semester','add_time']

class MyXuanKeAdmin(object):
    model_icon = 'fa fa-book'
    list_display=['lesson_teacher','student','lesson_type','point','delete_post_code']
    search_fields=['student__name','student__id','lesson_teacher__teacher__name','lesson_teacher__lesson__name','lesson_teacher__teacher__id','lesson_teacher__lesson__id']
    list_fields=['student__name','point','lesson_type','lesson_teacher__lesson__name','lesson_teacher__teacher__name']


xadmin.site.register(PingJiaoTeacher,PingJiaoTeacherAdmin)
xadmin.site.register(LessonLabels,LessonLabelsAdmin)
xadmin.site.register(StepOneLessonTeacher,StepOneLessonTeacherAdmin)
xadmin.site.register(MyXuanKe,MyXuanKeAdmin)