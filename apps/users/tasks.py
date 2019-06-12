#-*- coding:utf-8 -*-
from celery import shared_task
from logs.models import Log
from utils.address import get_address
from jwxzs_2.celery import app
import requests

from .models import Class,Colloge,Department,Student,Teacher,MyPassword
from utils.aes import return_my_words
from spiders.student_dynamic import SpiderDynamicStudent

from jwxzs_2.settings import MEDIA_ROOT

import time

@shared_task
def get_student_all_data(student_id):
    print(student_id)
    my_password=MyPassword.objects.get(user__username=student_id).password
    word=return_my_words(my_password)
    student=SpiderDynamicStudent(id=student_id,password=word)
    student.sign_in()
    student.get_all_data()



@shared_task
def login_log(ip,user_id):
    address=get_address(ip)
    Log.objects.create(user_id=user_id,ip=ip,address=address,action_type='other',message='登录了系统')
    print('结束')


@shared_task
def search_student_log(name,ip,user_id,student_id,gender,grade,colloge_id,class_id):
    # name = request._request.GET.get('name', '')
    if name:
        start_message='查询了'
        message_name = '姓名可能为" %s "' % name
        if gender:
            a='男' if gender=='male' else '女'
            message_gender='、性别为" %s "' % a
        else:
            message_gender=''
        if grade:
            message_grade='、年级为" %s "级' % grade
        else:
            message_grade=''
        if colloge_id:
            try:
                colloge_name=Colloge.objects.get(id=colloge_id).name
            except:
                colloge_name=colloge_id
            message_colloge='、学院为" %s "'%colloge_name
        else:
            message_colloge=''
        if class_id:
            try:
                class_name=Class.objects.get(id=colloge_id).name
            except:
                class_name=colloge_id
            message_cla='、班级为" %s "'%class_name
        else:
            message_cla=''
        end_message='的学生'
        message=start_message+message_name+message_gender+message_grade+message_colloge+message_cla+end_message
        print('开始插入')
        Log.objects.create(user_id=user_id,action_type='match',message=message,address=get_address(ip),ip=ip)
        print('插入完成！')
        # time.sleep(10)
    elif student_id:
        start_message = '查询了'
        message_id = '学号可能为" %s "' % student_id
        if gender:
            message_gender = '、性别为" %s "' % '男' if gender == 'male' else '女'
        else:
            message_gender = ''
        if grade:
            message_grade = '、年级为" %d "级' % grade
        else:
            message_grade = ''
        if colloge_id:
            try:
                colloge_name = Colloge.objects.get(id=colloge_id).name
            except:
                colloge_name = colloge_id
            message_colloge = '、学院为" %s "' % colloge_name
        else:
            message_colloge = ''
        if class_id:
            try:
                class_name = Class.objects.get(id=colloge_id).name
            except:
                class_name = colloge_id
            message_cla = '、班级为" %s "' % class_name
        else:
            message_cla = ''
        end_message = '的学生'
        message = start_message + message_id + message_gender + message_grade + message_colloge + message_cla + end_message
        print('开始插入')
        Log.objects.create(user_id=user_id, action_type='match', message=message, address=get_address(ip), ip=ip)
        print('插入完成！')
    else:
        print('未找到name')

@shared_task
def student_detail_log(ip,user_id):
    message='查询了我的详细个人信息'
    Log.objects.create(user_id=user_id, action_type='match', message=message, address=get_address(ip), ip=ip)



@shared_task
def search_teacher_log(ip,user_id,name,gender,department_id):
    if name:
        start_mess='查询了'
        name_mess='姓名为" %s "'%name
        if gender:
            gend="男" if gender=="male" else "女"
            gender_mess='、性别为" %s "'%gend
        else:
            gender_mess=''
        if department_id:
            department=Department.objects.get(id=department_id)
            depa_name_mess="、所在学院为' %s '"%department.name
        else:
            depa_name_mess=""
        end_mess="的老师"
        message = start_mess+name_mess+gender_mess+depa_name_mess+end_mess
        Log.objects.create(user_id=user_id,ip=ip, address=get_address(ip), action_type='match', message=message)



def get_student_photo(student,timeout=4,limit_time=5):
    try:
        url=r'http://jwc.jxnu.edu.cn/StudentPhoto/{}.jpg'.format(student.id)
        img_data = requests.get(url,timeout=timeout)
        if img_data.status_code==requests.codes.ok:
            src=MEDIA_ROOT+'/imgs/student/'+student.id+'.jpg'
            with open(src,'wb') as photo:
                photo.write(img_data.content)
                photo.close()
            img='imgs/student/'+student.id+'.jpg'
            student.image=img
            student.save()
            if not student.user.image:
                student.user.image=img
                student.user.save()
            print(student.image)
            return
        else:
            print('获取头像异常，url: ',url)
            return
    except:
        limit_ti = limit_time - 1
        if limit_ti > 0:
            print('get_student_photo timeout, retrying。。')
            return get_student_photo(student=student, limit_time=limit_ti)
        else:
            return None

@shared_task
def student_photo_task():
    students=Student.objects.all()
    for stu in students:
        get_student_photo(stu)


def get_teacher_photo(teacher,timeout=4,limit_time=5):
    try:
        url = r'http://jwc.jxnu.edu.cn/TeacherPhotos/{0}.jpg'.format(teacher.id)
        img_data = requests.get(url,timeout=timeout)
        if img_data.status_code==requests.codes.ok:
            src=MEDIA_ROOT+'imgs/teacher/'+teacher.id+'.jpg'
            with open(src,'wb') as photo:
                photo.write(img_data.content)
                photo.close()
            img='imgs/teacher/'+teacher.id+'.jpg'
            teacher.image=img
            teacher.save()
            if not teacher.user.image:
                teacher.user.image=img
                teacher.user.save()
            print(teacher.image)
            return
        else:
            print('获取头像异常，url: ',url)
            return
    except:
        limit_ti = limit_time - 1
        if limit_ti > 0:
            print('get_teacher_photo timeout, retrying。。')
            return get_teacher_photo(teacher=teacher, limit_time=limit_ti)
        else:
            return None

@shared_task
def teacher_photo_task():
    teachers=Teacher.objects.all()
    for tea in teachers:
        get_teacher_photo(tea)
