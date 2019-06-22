#-*- coding:utf-8 -*-
import xadmin
import os
import subprocess as sp

from .models import SpiderLog,SpiderLogDetail,Timer

# 设计左侧菜单
class GlobalSetting(object):  #名称不能改
    site_title = u'教务小助手后台管理系统'
    site_footer = u'教务小助手'
    menu_style = 'accordion'
    def get_site_menu(self):  #名称不能改
        return [
            {
                'title': '爬虫管理',
                'icon': 'fa fa-bug',
                'menus': (
                    {
                        'title': '爬取专业',
                        'url': '/xadmin/spider-major',
                        'icon': 'fa fa-bug',
                    },
                    {
                        'title': '爬取学院',
                        'url': '/xadmin/spider-colloge',
                        'icon': 'fa fa-bug',
                    },
                    {
                        'title':'爬取班级',
                        'url':'/xadmin/spider-class',
                        'icon':'fa fa-bug',
                    },
                    {
                        'title': '爬取学生',    #这里是你菜单的名称
                        'url': '/xadmin/spider-student',     #这里填写你将要跳转url
                        'icon': 'fa fa-bug',     #这里是bootstrap的icon类名，要换icon只要登录bootstrap官网找到icon的对应类名换上即可
                    },
                    {
                        'title': '爬取教师部门',
                        'url': '/xadmin/spider-department',
                        'icon': 'fa fa-bug',
                    },
                    {
                        'title': '爬取教师',
                        'url': '/xadmin/spider-teacher',
                        'icon': 'fa fa-bug',
                    },
                    {
                        'title': '爬取课表',
                        'url': '/xadmin/spider-schedule',
                        'icon': 'fa fa-bug',
                    },
                    {
                        'title': '爬取成绩',
                        'url': '/xadmin/spider-score',
                        'icon': 'fa fa-bug',
                    },
                    {
                        'title': '爬取最新成绩',
                        'url': '/xadmin/spider-new-score',
                        'icon': 'fa fa-bug',
                    },
                    # {
                    #     'title': '毕业生失效',
                    #     'url': '/xadmin/graduate-lose-efficacy',
                    #     'icon': 'fa fa-bug',
                    # },
                )
            },
            {
                'title': '更新数据',
                'icon': 'fa fa-calendar-o',
                'menus': (
                    {
                        'title': '毕业生失效',
                        'url': '/xadmin/graduate-lose-efficacy',
                        'icon': 'fa fa-calendar-o',
                    },
                    {
                        'title': '更新图数据库',
                        'url': '/xadmin/neo4j',
                        'icon': 'fa fa-calendar-o',
                    }
                )
            },
        ]

class SpiderLogAdmin(object):
    list_display=['desc','task_id','url','spider_class_and_method','start_time','stop_time','type','status','user','id']
    list_editable=['type','status']
    refresh_times = [3, 5, 10, 30, 60, 120]
    search_fields=['desc','spider_class_and_method','id']
    list_filter=['desc','spider_class_and_method','start_time','stop_time','status','user__name','user__username','type']
    model_icon = 'fa fa-bug'

class SpiderLogDetailAdmin(object):
    list_display=['desc','model','spider_log','status','create_time','id']
    refresh_times = [3, 5, 10, 30, 60, 120]
    search_fields=['id','desc','spider_log__desc']
    list_filter=['model','spider_log__desc','status','desc']
    model_icon='fa fa-bug'

class TimerAdmin(object):
    model_icon = 'fa fa-bug'
    list_display=['type','hours','id']
    # def has_add_permission(self):
    #     return False
    # def has_delete_permission(self):
    #     return False
    def save_models(self):
        obj = self.new_obj
        os.system('celery control shutdown')
        obj.save()
        # sp.call('celery -A jwxzs_2 worker -B -l info')
        # os.popen('celery -A jwxzs_2 worker -B -l info')
        # sp.Popen(['celery -A jwxzs_2 worker -B -l info',])
        sp.Popen('celery -A jwxzs_2 worker -B -l info',shell=True)
        # os.popen('ls')
        # os.system('nohup celery -A jwxzs_2 worker -B -l info')





    #注册你上面填写的url
from .views import SpiderMajorView,SpiderStudentView,SpiderCollogeView,SpiderClassView,SpiderTeacherView,SpiderDepartmentView,SpiderScheduleView,SpiderScoreView,SpiderNewScoreView\
    ,GraduateLoseEfficacyView,Neo4jView   #从你的app的view里引入你将要写的view，你也可以另外写一个py文件，把后台的view集中在一起方便管理
xadmin.site.register_view(r'spider-major/$', SpiderMajorView, name='spider-major')
xadmin.site.register_view(r'spider-student/$', SpiderStudentView, name='spider-student')
xadmin.site.register_view(r'spider-class/$', SpiderClassView, name='spider-class')
xadmin.site.register_view(r'spider-colloge/$', SpiderCollogeView, name='spider-colloge')
xadmin.site.register_view(r'spider-teacher/$', SpiderTeacherView, name='spider-teacher')
xadmin.site.register_view(r'spider-department/$', SpiderDepartmentView, name='spider-department')
xadmin.site.register_view(r'spider-schedule/$', SpiderScheduleView, name='spider-schedule')
xadmin.site.register_view(r'spider-score/$', SpiderScoreView, name='spider-score')
xadmin.site.register_view(r'spider-new-score/$', SpiderNewScoreView, name='spider-new-score')
xadmin.site.register_view(r'graduate-lose-efficacy/$',GraduateLoseEfficacyView, name='graduate-lose-efficacy')
xadmin.site.register_view(r'neo4j/$',Neo4jView, name='neo4j')

#注册GlobalSetting
from xadmin.views import CommAdminView
xadmin.site.register(CommAdminView, GlobalSetting)
xadmin.site.register(SpiderLog,SpiderLogAdmin)
xadmin.site.register(SpiderLogDetail,SpiderLogDetailAdmin)
xadmin.site.register(Timer,TimerAdmin)