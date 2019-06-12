#-*- coding:utf-8 -*-


import os,django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "jwxzs_2.settings")# project_name 项目名称
django.setup()
import requests

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


def get_student_photo(user,timeout=4,limit_time=5):
    try:
        if not user.image:
            url=r'http://jwc.jxnu.edu.cn/StudentPhoto/{}.jpg'.format(user.username)
            img_data = requests.get(url,timeout=timeout)
            if img_data.status_code==requests.codes.ok:
                with open('../media/imgs/student/'+user.username+'.jpg','wb') as photo:
                    photo.write(img_data.content)
                    photo.close()
                img='imgs/student/'+user.username+'.jpg'
                user.image=img
                user.save()
                print('保存成功！')
            else:
                print('头像下载失败！',user.username)
            return
        else:
            print('头像已存在')
            return
    except:
        limit_ti = limit_time - 1
        if limit_ti > 0:
            print('get_student_photo timeout, retrying。。')
            return get_student_photo(user=user,limit_time=limit_ti)
        else:
            return None

def create_all_student_photo():
    user=UserProfile.objects.filter(is_student=True)
    for u in user:
        get_student_photo(u)



def get_teacher_photo(user,timeout=4,limit_time=5):
    try:
        if not user.image:
            url=r'http://jwc.jxnu.edu.cn/TeacherPhotos/{}.jpg'.format(user.username)
            img_data = requests.get(url,timeout=timeout)
            if img_data.status_code==requests.codes.ok:
                with open('../media/imgs/teacher/'+user.username+'.jpg','wb') as photo:
                    photo.write(img_data.content)
                    photo.close()
                img='imgs/teacher/'+user.username+'.jpg'
                user.image=img
                user.save()
                print('保存成功！')
            else:
                print('头像下载失败！',user.username)
            return
        else:
            print('头像已存在')
            return
    except:
        limit_ti = limit_time - 1
        if limit_ti > 0:
            print('get_teacher_photo timeout, retrying。。')
            return get_teacher_photo(user=user,limit_time=limit_ti)
        else:
            return None

def create_all_teacher_photo():
    user=UserProfile.objects.filter(is_teacher=True)
    for u in user:
        get_teacher_photo(u)





if __name__ == '__main__':
    # create_all_teacher_photo()
    # create_all_student_user()
    # create_all_teacher_user()
    # user=UserProfile.objects.get(username='003550')
    # get_teacher_photo(user)
    create_all_student_photo()






