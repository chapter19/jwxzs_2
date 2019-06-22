#-*- coding:utf-8 -*-

from celery import shared_task
from datetime import datetime
import time

from spiders.student_static import SpiderStaticStudent
from spiders.teacher_static import SpiderStaticTeacher
from spiders.student_dynamic import SpiderDynamicStudent
from utils.settings import MY_WORD,MY_USERNAME
from .models import SpiderLog
from users.models import Colloge,MyPassword
from utils.aes import return_my_words


@shared_task
def get_major(log_id,grade):
    log=SpiderLog.objects.get(id=log_id)
    log.status='getting'
    log.save()
    spd = SpiderStaticStudent(MY_USERNAME, MY_WORD)
    spd.sign_in()
    spd.get_one_grade_major(log_id=log.id,grade_post_code=grade)
    log.status='end'
    log.save()

@shared_task
def get_class(log_id,colloge_post_code=None,grade=None,if_all_colloge=False,if_all_grade=False):
    if if_all_colloge:
        if if_all_grade:
            log=SpiderLog.objects.get(id=log_id)
            log.status='getting'
            log.save()
            log.spider_class_and_method='SpiderStaticStudent.get_class_from_all_colloge(log_id={0})'.format(log.id)
            log.save()
            spd = SpiderStaticStudent(MY_USERNAME, MY_WORD)
            spd.sign_in()
            spd.get_class_from_all_colloge(log_id=log.id)
            log.status='end'
            log.stop_time=datetime.now()
            log.save()
        else:
            log = SpiderLog.objects.get(id=log_id)
            log.status = 'getting'
            log.save()
            log.spider_class_and_method = 'SpiderStaticStudent.get_one_grade_class_from_all_colloge(grade="{0}",log_id={1})'.format(grade,log.id)
            log.save()
            spd = SpiderStaticStudent(MY_USERNAME, MY_WORD)
            spd.sign_in()
            spd.get_one_grade_class_from_all_colloge(grade=grade,log_id=log.id)
            log.status = 'end'
            log.stop_time = datetime.now()
            log.save()
    else:
        if if_all_grade:
            log = SpiderLog.objects.get(id=log_id)
            log.status = 'getting'
            log.save()
            log.spider_class_and_method='SpiderStaticStudent.get_class(colloge_post_code="{0}",log_id={1})'.format(colloge_post_code,log.id)
            log.save()
            spd = SpiderStaticStudent(MY_USERNAME, MY_WORD)
            spd.sign_in()
            spd.get_one_colloge_classes(colloge_code=colloge_post_code,log_id=log.id)
            log.status = 'end'
            log.stop_time = datetime.now()
            log.save()
        else:
            log = SpiderLog.objects.get(id=log_id)
            log.status = 'getting'
            log.save()
            log.spider_class_and_method = 'SpiderStaticStudent.get_one_colloge_one_grade_classes(grade="{0}",colloge_code="{1}",log_id={2})'.format(grade,colloge_post_code,log.id)
            log.save()
            try:
                spd = SpiderStaticStudent(MY_USERNAME, MY_WORD)
                spd.sign_in()
                spd.get_one_colloge_one_grade_classes(grade=grade,colloge_code=colloge_post_code,log_id=log.id)
                log.status = 'end'
                log.stop_time = datetime.now()
            except:
                log.status='error'
            log.save()

@shared_task
def get_student(log_id,colloge_post_code,grade):
    if colloge_post_code=='all':
        if grade=='all':
            log = SpiderLog.objects.get(id=log_id)
            log.status = 'getting'
            log.save()
            spd = SpiderStaticStudent(MY_USERNAME, MY_WORD)
            spd.sign_in()
            spd.get_colloge_grade_student(log_id=log.id,colloge_post_code='all',grade='all')
            log.status = 'end'
            log.stop_time = datetime.now()
            log.save()
        else:
            log = SpiderLog.objects.get(id=log_id)
            log.status = 'getting'
            log.save()
            spd = SpiderStaticStudent(MY_USERNAME, MY_WORD)
            spd.sign_in()
            spd.get_colloge_grade_student(log_id=log.id, colloge_post_code='all', grade=grade)
            log.status = 'end'
            log.stop_time = datetime.now()
            log.save()
    else:
        if grade=='all':
            log = SpiderLog.objects.get(id=log_id)
            log.status = 'getting'
            log.save()
            spd = SpiderStaticStudent(MY_USERNAME, MY_WORD)
            spd.sign_in()
            spd.get_colloge_grade_student(log_id=log.id,colloge_post_code=colloge_post_code,grade='all')
            log.status = 'end'
            log.stop_time = datetime.now()
            log.save()
        else:
            log = SpiderLog.objects.get(id=log_id)
            log.status = 'getting'
            log.save()
            spd = SpiderStaticStudent(MY_USERNAME, MY_WORD)
            spd.sign_in()
            spd.get_colloge_grade_student(log_id=log.id, colloge_post_code=colloge_post_code, grade=grade)
            log.status = 'end'
            log.stop_time = datetime.now()
            log.save()

@shared_task
def get_teacher(log_id,department_post_code):
    if department_post_code=='all':
        log = SpiderLog.objects.get(id=log_id)
        log.status = 'getting'
        log.save()
        spd = SpiderStaticTeacher(MY_USERNAME, MY_WORD)
        spd.sign_in()
        spd.get_teacher(log_id=log.id)
        log.status = 'end'
        log.stop_time = datetime.now()
        log.save()
    else:
        log = SpiderLog.objects.get(id=log_id)
        log.status = 'getting'
        log.save()
        spd = SpiderStaticTeacher(MY_USERNAME, MY_WORD)
        spd.sign_in()
        spd.get_one_colloge_teachers(post_code=department_post_code,log_id=log.id)
        log.status = 'end'
        log.stop_time = datetime.now()
        log.save()

@shared_task
def get_department(log_id):
    log = SpiderLog.objects.get(id=log_id)
    log.status = 'getting'
    log.save()
    spd = SpiderStaticTeacher(MY_USERNAME, MY_WORD)
    spd.sign_in()
    spd.get_department(log_id=log.id)
    log.status = 'end'
    log.stop_time = datetime.now()
    log.save()

@shared_task
def get_colloge(log_id):
    log = SpiderLog.objects.get(id=log_id)
    log.status = 'getting'
    log.save()
    spd = SpiderStaticStudent(MY_USERNAME, MY_WORD)
    spd.sign_in()
    spd.get_colloges(log_id=log.id)
    log.status = 'end'
    log.stop_time = datetime.now()
    log.save()

@shared_task
def get_schedule(log_id,semester):
    if semester=='all':
        log = SpiderLog.objects.get(id=log_id)
        log.status = 'getting'
        log.save()
        spd = SpiderStaticTeacher(MY_USERNAME, MY_WORD)
        spd.sign_in()
        spd.get_schedule(log_id=log.id)
        log.status = 'end'
        log.stop_time = datetime.now()
        log.save()
    else:
        log = SpiderLog.objects.get(id=log_id)
        log.status = 'getting'
        log.save()
        spd = SpiderStaticTeacher(MY_USERNAME, MY_WORD)
        spd.sign_in()
        spd.get_one_semester_schedule(log_id=log.id,semester=semester)
        log.status = 'end'
        log.stop_time = datetime.now()
        log.save()

@shared_task
def get_score(log_id):
    log = SpiderLog.objects.get(id=log_id)
    log.status = 'getting'
    log.save()
    my_passwords=MyPassword.objects.filter(user__is_active=True,user__is_student=True)
    if my_passwords:
        for stu in my_passwords:
            word=return_my_words(stu.password)
            spd=SpiderDynamicStudent(id=stu.user.username,password=word)
            sign_in=spd.sign_in()
            if sign_in:
                spd.get_my_studyData()
            else:
                pass
    log.status='end'
    log.stop_time=datetime.now()
    log.save()

@shared_task
def get_new_score(log_id):
    log = SpiderLog.objects.get(id=log_id)
    log.status = 'getting'
    log.save()
    my_passwords = MyPassword.objects.filter(user__is_active=True, user__is_student=True)
    if my_passwords:
        for stu in my_passwords:
            word = return_my_words(stu.password)
            spd = SpiderDynamicStudent(id=stu.user.username, password=word)
            sign_in = spd.sign_in()
            if sign_in:
                spd.get_new_score()
            else:
                pass
    log.status = 'end'
    log.stop_time = datetime.now()
    log.save()

@shared_task
def post_task_id(verbose_id,task_id):
    count=0
    while True:
        log=SpiderLog.objects.filter(verbose_id=verbose_id)
        if log:
            log=log[0]
            log.task_id=task_id
            log.save()
            break
        else:
            count+=1
            if count>15:
                break
            time.sleep(1)