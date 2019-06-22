#-*- coding:utf-8 -*-
from celery import shared_task
from datetime import datetime

from users.models import UserProfile,Major
from .models import UpdateLog
from neo4j.create_graph import JwxzsGraph

@shared_task
def graduate_lose_efficacy(log_id,grade):
    log=UpdateLog.objects.get(id=log_id)
    log.class_and_method='graduate_lose_efficacy(log_id={0},grade={1})'.format(log_id,grade)
    log.status='getting'
    log.save()
    user=UserProfile.objects.filter(is_student=True,student__cla__grade=grade)
    if user:
        for u in user:
            stu=u.student
            if stu.is_active:
                stu.is_active=False
                stu.save()
            if u.is_active:
                u.is_active=False
                u.save()
                print('has lose efficacy')
            else:
                print('not active')
    major=Major.objects.filter(grade=grade)
    for m in major:
        m.is_active=False
        m.save()
    log.status='end'
    log.stop_time=datetime.now()
    log.save()

@shared_task
def update_neo4j(log_id,semester):
    log = UpdateLog.objects.get(id=log_id)
    log.class_and_method = 'JwxzsGraph.update_all(log_id={0},semester={1})'.format(log_id,semester)
    log.status = 'getting'
    log.save()
    g=JwxzsGraph()
    g.update_all(semester=semester)
    # g.create_all_student_node()
    # g.create_all_teacher_node()
    # g.create_lesson_node()
    # g.create_major_node()
    # g.create_tea_stu_rela()
    # g.create_stu_less_rela()
    # g.create_tea_less_rela()
    # g.create_stu_maj_rela()
    # g.create_maj_less_rela()

    log.status = 'end'
    log.stop_time = datetime.now()
    log.save()


