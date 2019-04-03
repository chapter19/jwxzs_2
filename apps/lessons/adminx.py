import xadmin

from .models import Lesson,Schedule,ScheduleLesson,MajorLesson

from xadmin import views

class LessonAdmin(object):
    list_display=['name','id','credit','if_public_elective','add_time']
    search_fields=['name','id']
    list_filter=['name','id','credit','if_public_elective','add_time']
    list_editable=['name','credit','if_public_elective']
    # readonly_fields=['id',]
    refresh_times=[5,10,30,60,120]


class MajorLessonAdmin(object):
    list_display=['lesson','major','lesson_type','if_degree','add_time']
    search_fields=['lesson__name','major__name','lesson_type','if_degree']
    list_filter=['major__grade','lesson_type','if_degree','add_time']
    list_editable=['lesson_type','if_degree',]
    raw_id_fields = ('lesson',)
    refresh_times = [5, 10, 30, 60, 120]


class ScheduleLessonAdmin(object):
    list_display=['lesson','class_id','class_name','semester','teacher','add_time']
    search_fields=['lesson__name','lesson__id','class_id','class_name','semester','teacher__name','teacher__id']
    list_filter=['semester','teacher__name','teacher__id','add_time']
    # 编辑页外键 搜索
    raw_id_fields = ('lesson',)
    #在列表显示页可编辑
    list_editable = ['lesson_type', 'if_degree', ]
    refresh_times = [5, 10, 30, 60, 120]


class ScheduleAdmin(object):
    list_display=['schedule_lesson','counter','class_room','add_time']
    search_fields=['schedule_lesson__lesson__name','counter','class_room']
    list_filter=['schedule_lesson','counter','class_room','add_time','schedule_lesson__semester']
    refresh_times = [5, 10, 30, 60, 120]


xadmin.site.register(Lesson,LessonAdmin)
xadmin.site.register(ScheduleLesson,ScheduleLessonAdmin)
xadmin.site.register(Schedule,ScheduleAdmin)
xadmin.site.register(MajorLesson,MajorLessonAdmin)




