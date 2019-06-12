#-*- coding:utf-8 -*-
from celery import shared_task
from logs.models import Log
from utils.address import get_address

from .models import ScheduleLesson
from semesters.models import Semester
from users.models import Student,Teacher

@shared_task
def student_schedule_log(ip,user_id,student_id,semester,username):
    if student_id:
        if semester:
            seme=Semester.objects.get(post_code=semester)
            if student_id==username:
                message='查询了我的" %s "的课程表'%seme.verbose_name
            else:
                stu=Student.objects.get(id=student_id)
                message='查询了学生" %s "的" %s "的课程表'%(stu.name,seme.verbose_name)
            Log.objects.create(ip=ip,address=get_address(ip),user_id=user_id,message=message,action_type='match')


@shared_task
def teacher_schedule_log(ip,user_id,teacher_id,semester,username):
    if teacher_id:
        if semester:
            seme=Semester.objects.get(post_code=semester)
            if teacher_id==username:
                message='查询了我的" %s "的课程表'%seme.verbose_name
            else:
                stu=Teacher.objects.get(id=teacher_id)
                message='查询了教师" %s "的" %s "的课程表'%(stu.name,seme.verbose_name)
            Log.objects.create(ip=ip,address=get_address(ip),user_id=user_id,message=message,action_type='match')
