#-*- coding:utf-8 -*-
import os,django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "jwxzs_2.settings")# project_name 项目名称
django.setup()

from users.models import UserProfile,Student,Teacher


def student_image():
    students=Student.objects.all()
    for stu in students:
        try:
            stu.image=stu.user.image
            stu.save()
            print(stu.image)
        except:
            print('学生照片异常')

def teacher_image():
    teachers=Teacher.objects.all()
    for tea in teachers:
        try:
            tea.image=tea.user.image
            tea.save()
            print(tea.image)
        except:
            print('教师照片异常')

if __name__ == '__main__':
    teacher_image()
    student_image()