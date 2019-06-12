#-*- coding:utf-8 -*-
from celery import shared_task

from .models import Homework,HomeworkScore,Question,StudentChoiceAnswer,ChoiceTrueAnswer,QuestionScore,PanDuanTrueAnswer,\
    StudentPanDuanAnswer,TianKongBlank,TianKongOtherAnswer,TianKongTrueAnswer,StudentTianKongAnswer,StudentJianDaAnswer,StudentDaiMaAnswer,StudentOtherAnswer
from scores.models import Score

@shared_task
def auto_correct(homework_id,student_id):
    homework=Homework.objects.get(id=homework_id)
    homework_score=HomeworkScore.objects.filter(student_id=student_id,homework=homework)[0]
    questions = Question.objects.filter(homework=homework, if_auto_correct=True)
    for q in questions:
        if q.question_type=='DanXuan':
            s_c_a=StudentChoiceAnswer.objects.filter(student_id=student_id,question=q)
            if s_c_a:
                s_c_a=s_c_a[0]
                c_t_a=ChoiceTrueAnswer.objects.filter(question=q)
                if s_c_a.choice==c_t_a[0].choice:
                    QuestionScore.objects.create(student_id=student_id, question=q, score=q.score)
                    homework_score+=q.score
                else:
                    QuestionScore.objects.create(student_id=student_id, question=q, score=0)
            else:
                QuestionScore.objects.create(student_id=student_id,question=q,score=0,if_no_answer=True)
        elif q.question_type=='DuoXuan':
            s_c_a=StudentChoiceAnswer.objects.filter(student_id=student_id,question=q)
            if s_c_a:
                c_t_a = ChoiceTrueAnswer.objects.filter(question=q)
                lenth=len(c_t_a)
                if lenth!=len(s_c_a):
                    QuestionScore.objects.create(student_id=student_id, question=q, score=0)
                else:
                    is_true=True
                    for i in range(lenth):
                        if s_c_a[i]!=c_t_a[i]:
                            is_true=False
                    if is_true:
                        QuestionScore.objects.create(student_id=student_id, question=q, score=q.score)
                        homework_score += q.score
                    else:
                        QuestionScore.objects.create(student_id=student_id, question=q, score=0)
            else:
                QuestionScore.objects.create(student_id=student_id, question=q, score=0,if_no_answer=True)
        elif q.question_type=='PanDuan':
            s_p_a=StudentPanDuanAnswer.objects.filter(student_id=student_id,question=q)
            if s_p_a:
                s_p_a=s_p_a[0]
                p_t_a=PanDuanTrueAnswer.objects.get(question=q)
                if s_p_a.answer!=p_t_a.answer:
                    QuestionScore.objects.create(student_id=student_id, question=q, score=0)
                else:
                    QuestionScore.objects.create(student_id=student_id, question=q, score=q.score)
                    homework_score += q.score
            else:
                QuestionScore.objects.create(student_id=student_id, question=q, score=0,if_no_answer=True)
        elif q.question_type=='TianKong':
            blanks=TianKongBlank.objects.filter(question=q)
            s=0
            an=0
            for bl in blanks:
                t_t_a=bl.tiankong_true_answer
                s_t_a=StudentTianKongAnswer.objects.filter(student_id=student_id,blank=bl)
                if s_t_a:
                    an+=len(s_t_a)
                    s_t_a=s_t_a[0]
                    if bl.if_other_answer:
                        if t_t_a.answer==s_t_a.answer:
                            s+=bl.score
                        else:
                            t_o_a=TianKongOtherAnswer.objects.filter(blank=bl)
                            for o_a in t_o_a:
                                if o_a.other_answer==s_t_a.answer:
                                    s+=bl.score
                                    break
                    else:
                        if t_t_a.answer==s_t_a.answer:
                            s+=bl.score
            if an>0:
                QuestionScore.objects.create(student_id=student_id, question=q, score=s)
            else:
                QuestionScore.objects.create(student_id=student_id, question=q, score=s,if_no_answer=True)
    homework_score.save()

@shared_task
def auto_correct_no_submit_homework(homework_id):
    homework=Homework.objects.get(id=homework_id)
    schedule_lesson=homework.lesson_period.schedule_lesson
    score=Score.objects.filter(schedule_lesson=schedule_lesson)
    if score:
        for s in score:
            homework_score=HomeworkScore.objects.filter(homework=homework,student=s.student)
            if homework_score:
                question = Question.objects.filter(homework=homework)
                if question:
                    for q in question:
                        type=q.question_type
                        if type=='DanXuan' or type=='DuoXuan':
                            student_choice_answer=StudentChoiceAnswer.objects.filter(student=s.student,question=q)
                            if not student_choice_answer:
                                QuestionScore.objects.create(student=s.student, question=q, if_no_answer=True)
                        elif type=='PanDuan':
                            student_panduan_answer=StudentPanDuanAnswer.objects.filter(student=s.student,question=q)
                            if not student_panduan_answer:
                                QuestionScore.objects.create(student=s.student, question=q, if_no_answer=True)
                        elif type=='TianKong':
                            student_tiankong_answer=StudentTianKongAnswer.objects.filter(blank__question=q,student=s.student)
                            if not student_tiankong_answer:
                                QuestionScore.objects.create(student=s.student, question=q, if_no_answer=True)
                        elif type=='JianDa':
                            student_jianda_answer=StudentJianDaAnswer.objects.filter(student=s.student,question=q)
                            if not student_jianda_answer:
                                QuestionScore.objects.create(student=s.student, question=q, if_no_answer=True)
                        elif type=='DaiMa':
                            student_daima_answer=StudentDaiMaAnswer.objects.filter(student=s.student,daima_file__question=question,if_auto_submit=False)
                            if not student_daima_answer:
                                QuestionScore.objects.create(student=s.student, question=q, if_no_answer=True)
                        elif type=='QiTa':
                            student_other_answer=StudentOtherAnswer.objects.filter(student=s.student,question=q)
                            if not student_other_answer:
                                QuestionScore.objects.create(student=s.student, question=q, if_no_answer=True)
            else:
                HomeworkScore.objects.create(homework=homework, student=s.student,if_no_answer=True)
                question=Question.objects.filter(homework=homework)
                if question:
                    for q in question:
                        QuestionScore.objects.create(student=s.student,question=q,if_no_answer=True)

