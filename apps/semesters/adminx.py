#-*- coding:utf-8 -*-

import xadmin
from .models import Semester,CurrentSemester,NextSemester,Grade


class SemesterAdmin(object):
    list_display=['verbose_name','post_code']
    model_icon='fa fa-list'
    def save_models(self):
        obj=self.new_obj
        if not obj.post_code:
            # 15-16第1学期
            # 2015/9/1 0:00:00
            v_n=obj.verbose_name.strip()
            if v_n[-3]=='1':
                obj.post_code='20'+v_n[0:2]+'/9/1 0:00:00'
                obj.save()
            elif v_n[-3]=='2':
                obj.post_code='20'+v_n[3:5]+'/3/1 0:00:00'
                obj.save()
        else:
            obj.save()


class CurrentSemesterAdmin(object):
    model_icon = 'fa fa-list'
    display_list=['current_semester']


class NextSemesterAdmin(object):
    model_icon = 'fa fa-list'
    display_list=['next_semester']

class GradeAdmin(object):
    model_icon = 'fa fa-list'
    list_display=['grade','semester']

xadmin.site.register(Semester,SemesterAdmin)
xadmin.site.register(CurrentSemester,CurrentSemesterAdmin)
xadmin.site.register(NextSemester,NextSemesterAdmin)
xadmin.site.register(Grade,GradeAdmin)