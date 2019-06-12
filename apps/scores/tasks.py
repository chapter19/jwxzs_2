#-*- coding:utf-8 -*-

from celery import shared_task
from logs.models import Log
from utils.address import get_address

from .models import ScheduleLesson
from semesters.models import Semester
from users.models import Student
from spiders.student_dynamic import SpiderDynamicStudent

@shared_task
def student_scores_log(ip,user_id,student_id,semester,if_major):
    if student_id:
        if semester:
            seme = Semester.objects.get(post_code=semester)
            if if_major:
                maj_mess='专业课'
            else:
                maj_mess=''
            message = '查询了" %s "的%s成绩'%(seme.verbose_name,maj_mess)
            Log.objects.create(user_id=user_id,ip=ip,address=get_address(ip),action_type='match',message=message)

@shared_task
def teacher_scores_log(ip,user_id,student_id,semester,if_major):
    if student_id:
        if semester:
            seme = Semester.objects.get(post_code=semester)
            if if_major:
                maj_mess = '专业课'
            else:
                maj_mess = ''
            stu=Student.objects.get(id=student_id)
            message = '查询了学生" %s "的" %s "的%s成绩' % (stu.name,seme.verbose_name, maj_mess)
            Log.objects.create(user_id=user_id, ip=ip, address=get_address(ip), action_type='match', message=message)


@shared_task
def student_total_credit_log(ip,user_id,student_id):
    if student_id:
        message='查询了我的学习成绩概述'
        Log.objects.create(user_id=user_id,ip=ip,address=get_address(ip),action_type='match',message=message)


@shared_task
def teacher_total_credit_log(ip,user_id,student_id):
    if student_id:
        stu=Student.objects.get(id=student_id)
        message='查询了学生" %s "的学习成绩概述'%stu.name
        Log.objects.create(user_id=user_id,ip=ip,address=get_address(ip),action_type='match',message=message)



@shared_task
def schedule_student_list_log(ip,user_id,sch_les_id):
    if sch_les_id:
        sch_less=ScheduleLesson.objects.get(id=sch_les_id)
        semes=Semester.objects.get(post_code=sch_less.semester)
        message=' 查询了" %s "的" %s "的" %s "的课表的学生名单 '%(semes.verbose_name,sch_less,sch_less.class_name)
        Log.objects.create(user_id=user_id,ip=ip,address=get_address(ip),action_type='match',message=message)




@shared_task
def update_score(student_id,password):
    spd=SpiderDynamicStudent(student_id,password)
    spd.sign_in()
    spd.get_my_studyData()













