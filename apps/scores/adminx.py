#-*- coding:utf-8 -*-

import xadmin

from .models import Score,NewScore,TotalCredit

from xadmin import views


class ScoreAdmin(object):
    list_display=['schedule_lesson','student','score','standard_score','if_major','rescore','add_time']
    # search_fields=['schedule_lesson__lesson__name','schedule_lesson__lesson__id','student__name','student__id','schedule_lesson__teacher__name','schedule_lesson__teacher__id']
    search_fields=['student__name','student__id','schedule_lesson__teacher__id']
    list_filter=['score','standard_score','rescore','if_major','add_time','student__name','schedule_lesson__teacher__name','schedule_lesson__semester']
    list_editable=['score','standard_score','if_major','rescore']
    refresh_times = [5, 10, 30, 60, 120]


class NewScoreAdmin(object):
    list_display=['schedule_lesson','student','algorithm','daily_score','practical_score','theoretical_score','score','if_major','add_time']
    seacher_fields=['student__name','student__id']
    list_filter=['score','if_major','student__name','schedule_lesson__teacher__name','schedule_lesson__semester','add_time']
    refresh_times = [5, 10, 30, 60, 120]


class TotalCreditAdmin(object):
    list_display=['student','credit','standard_score']
    seacher_fields = ['student__name', 'student__id']
    list_filter=['student__gender','student__cla__grade','student__cla__name','student__name','credit','standard_score']
    list_editable=['standard_score','credit',]
    # 外键搜索
    raw_id_fields = ('student',)
    refresh_times = [5, 10, 30, 60, 120]

xadmin.site.register(Score,ScoreAdmin)
xadmin.site.register(NewScore,NewScoreAdmin)
xadmin.site.register(TotalCredit,TotalCreditAdmin)
