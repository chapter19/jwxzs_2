# -*- coding:utf-8 -*-

import xadmin

from .models import Colloge,Class,Student,Teacher,Department,Major,UserProfile,StudentDetail
from xadmin import views


class BaseSetting(object):
    enable_themes=True
    use_bootswatch=True


class GlobalSettings(object):
    site_title=u'教务小助手后台管理系统'
    site_footer=u'教务小助手'
    menu_style='accordion'


class MajorAdmin(object):
    list_display=['name','grade','major_id','add_time']
    search_fields=['name','grade','major_id']
    list_filter=['name','grade','major_id','add_time']
    readonly_fields = ['id']
    refresh_times = [5, 10, 30, 60, 120]


class CollogeAdmin(object):
    list_display=['name','id','post_code','add_time','get_class_nums']
    search_fields=['id','name','post_code']
    list_filter=['id','name','post_code','add_time']
    readonly_fields = ['id', 'post_code']
    refresh_times = [5, 10, 30, 60, 120]


class ClassAdmin(object):
    list_display = ['name', 'id', 'post_code','grade','colloge','add_time','major','get_student_nums']
    search_fields = ['id', 'name', 'post_code','grade','colloge__name','major__name']
    list_filter = ['id', 'name', 'post_code','grade','colloge','add_time','major']
    #下拉框变成可搜索
    relfield_style='fk_ajax'
    readonly_fields = ['id','post_code']
    ordering = ['-name']
    refresh_times = [5, 10, 30, 60, 120]


class StudentAdmin(object):
    list_display = ['name','id', 'cla','gender','add_time']
    search_fields = ['id', 'name', 'cla__colloge__name','cla__name','gender','cla__grade','cla__id','cla__colloge__id']
    list_filter = ['name', 'cla','cla__colloge','gender','add_time','cla__grade']
    #只读
    readonly_fields=['id']
    #排序
    ordering=['-id']
    #不显示
    exclude=['']
    # model_icon="fal fa-female"
    refresh_times = [5, 10, 30, 60, 120]


class DepartmentAdmin(object):
    list_display = ['name','id', 'post_code', 'add_time','get_teacher_nums']
    search_fields = ['id', 'name', 'post_code']
    list_filter = ['name','add_time']
    readonly_fields = ['id','post_code']
    refresh_times = [5, 10, 30, 60, 120]


class TeacherAdmin(object):
    list_display = ['name','id','gender','department', 'add_time']
    search_fields = ['id', 'name',  'gender','department__name']
    list_filter = ['name', 'gender','department', 'add_time']
    readonly_fields = ['id']
    ordering = ['id']
    refresh_times = [5, 10, 30, 60, 120]


class UserProfileAdmin(object):
    list_display=['username','name','id','gender','is_student','is_teacher','last_login','date_joined']
    search_fields=['username','name']
    list_filter=['gender','is_student','is_teacher','name','last_login','date_joined']
    refresh_times = [5, 10, 30, 60, 120]


class StudentDetailAdmin(object):
    list_display=['base_data','candidate_id','birthday','id_card','mobile','add_time']
    search_fields=['base_data__name','base_data__id','id_card','mobile','candidate_id','email']
    list_filter=['nationality','birthday','political_status','birthplace','add_time']
    refresh_times = [5, 10, 30, 60, 120]



xadmin.site.register(Colloge,CollogeAdmin)
xadmin.site.register(Class,ClassAdmin)
xadmin.site.register(Student,StudentAdmin)
xadmin.site.register(Department,DepartmentAdmin)
xadmin.site.register(Teacher,TeacherAdmin)
xadmin.site.register(Major,MajorAdmin)

# xadmin.site.unregister(UserProfile)
# xadmin.site.register(UserProfile,UserProfileAdmin)
xadmin.site.register(StudentDetail,StudentDetailAdmin)


xadmin.site.register(views.BaseAdminView,BaseSetting)
xadmin.site.register(views.CommAdminView,GlobalSettings)