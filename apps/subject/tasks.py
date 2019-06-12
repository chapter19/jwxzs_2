#-*- coding:utf-8 -*-
from celery import shared_task
from logs.models import Log
from utils.address import get_address
from jwxzs_2.celery import app

from .models import PingJiaoTeacher
from semesters.models import CurrentSemester


@shared_task
def pingjiao_list_create_pingjiaoteacher(student_id,data):
    for d in data:
        current_semester=CurrentSemester.objects.first()
        # print(d)
        try:
            PingJiaoTeacher.objects.create(student_id=student_id,teacher_id=d['teacher']['id'],lesson_name=d['lesson_name'],semester=current_semester.current_semester,code=d['code'])
        except:
            print('评教老师已存在')

@shared_task
def update_pingjiao(pjt,liA,groupB,groupC,groupD):
    if liA:
        for a in liA:
            pjt.filter(code=a).update(grade='groupA')
    if groupB:
        liB = groupB.split('|')[:-1]
        for b in liB:
            pjt.filter(code=b).update(grade='groupB')
    if groupC:
        liC = groupC.split('|')[:-1]
        for c in liC:
            pjt.filter(code=c).update(grade='groupC')
    if groupD:
        liD = groupD.split('|')[:-1]
        for d in liD:
            pjt.filter(code=d).update(grade='groupD')
    # for d in data:
    #     pjt.filter(lesson_name=d['lesson_name']).update(score=float(d['grade']))






