#-*- coding:utf-8 -*-
import os, django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "jwxzs_2.settings")  # project_name 项目名称
django.setup()

from lessons.models import Lesson
from users.models import Colloge
from spiders.subject_system import XuanKe

def update_lesson():
    lessons=Lesson.objects.all()
    for les in lessons:
        xuanke = XuanKe()
        xuanke.login()
        info=xuanke.get_lesson_information(kch=les.id)
        if info:
            # if not les.admin_department:
            if info['admin_department']!='免费师范生院':
                admin_department=Colloge.objects.filter(name=info['admin_department'])
                if admin_department:
                    admin_department=admin_department[0]
                else:
                    admin_department=None
            else:
                admin_department=Colloge.objects.get(id='57000')
            les.admin_department=admin_department
            if not les.open_semester:
                les.open_semester=info['open_semester'] if info['open_semester'] else None
            if not les.before_learning_text:
                les.before_learning_text=info['before_learning_text'] if info['before_learning_text'] else None
            if not les.profile:
                les.profile=info['profile'] if info['profile'] else None
            les.save()
            print(les)

def clean_department():
    lessons = Lesson.objects.all()
    for les in lessons:
        if les.admin_department_id=='57000':
            les.admin_department=None
            les.save()
            print(les)
        else:
            print('非免院')

if __name__ == '__main__':
    update_lesson()
    # clean_department()