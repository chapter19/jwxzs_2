import xadmin

from .models import Lesson,Schedule,ScheduleLesson,MajorLesson

from xadmin import views

class LessonAdmin(object):
    list_display=['name','id','credit','if_public_elective','add_time']
    search_fields=['name','id']
    list_filter=['name','id','credit','if_public_elective','add_time']


class MajorLessonAdmin(object):
    list_display=['lesson','major','lesson_type','if_degree','add_time']
    search_fields=['lesson__name','major__name','lesson_type','if_degree']
    list_filter=['major__grade','lesson_type','if_degree','add_time']


class ScheduleLessonAdmin(object):
    list_display=['lesson','class_id','class_name','semester','teacher','add_time']
    search_fields=['lesson__name','lesson__id','class_id','class_name','semester','teacher__name','teacher__id']
    list_filter=['semester','teacher__name','teacher__id','add_time']
    raw_id_fields = ('lesson',)


class ScheduleAdmin(object):
    list_display=['schedule_lesson','counter','class_room','add_time']
    search_fields=['schedule_lesson__lesson__name','counter','class_room']
    list_filter=['schedule_lesson','counter','class_room','add_time','schedule_lesson__semester']


xadmin.site.register(Lesson,LessonAdmin)
xadmin.site.register(ScheduleLesson,ScheduleLessonAdmin)
xadmin.site.register(Schedule,ScheduleAdmin)
xadmin.site.register(MajorLesson,MajorLessonAdmin)




