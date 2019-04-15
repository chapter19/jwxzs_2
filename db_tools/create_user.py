#-*- coding:utf-8 -*-


import os,django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "jwxzs_2.settings")# project_name 项目名称
django.setup()

from users.models import Student,Teacher,UserProfile
from jwxzs_2.settings import PUBLIC_PASSWORD
# from django.contrib.auth.hashers import make_password



# stu1=Student.objects.get(id='201626703077')
# stu2=Student.objects.get(id='201626703078')

def create_all_student_user():
    students=Student.objects.all()
    for stu in students:
        try:
            user=UserProfile(username=stu.id,password=PUBLIC_PASSWORD,is_student=True,is_active=False,name=stu.name,gender=stu.gender)
            user.save()
        except:
            user=UserProfile.objects.get(username=stu.id)
            user.name=stu.name
            user.gender=stu.gender
            user.save()
            print('id:',stu.id,' 已存在')
        # stu.user=user
        # stu.save()


def create_all_teacher_user():
    teachers=Teacher.objects.all()
    for tea in teachers:
        try:
            user=UserProfile(username=tea.id,password=PUBLIC_PASSWORD,is_teacher=True,is_active=False,name=tea.name,gender=tea.gender)
            user.save()
        except:
            user=UserProfile.objects.get(username=tea.id)
            print('id:',tea.id,' 已存在')
        tea.user=user
        tea.save()



if __name__ == '__main__':
    # create_all_student_user()
    create_all_teacher_user()







