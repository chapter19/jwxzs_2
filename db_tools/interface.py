#-*- coding:utf-8 -*-

import os,django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "jwxzs_2.settings")# project_name 项目名称
django.setup()

from users.models import UserProfile


def test():
    me=UserProfile.objects.get(username='201626703079')
    me.image='http://jwc.jxnu.edu.cn/StudentPhoto/201626703079.jpg'
    me.save()




















