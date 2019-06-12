#-*- coding:utf-8 -*-
import xadmin

from .models import KnowledgeLabel,Unit,LessonPeriod,Homework,Question,\
    QuestionImage,DaiMaFile,Choice,ChoiceTrueAnswer,StudentChoiceAnswer,\
    PanDuanTrueAnswer,StudentPanDuanAnswer,TianKongBlank,TianKongTrueAnswer,\
    TianKongOtherAnswer,StudentTianKongAnswer,JianDaAnswer,StudentJianDaAnswer,\
    OtherAnswer,OtherAnswerImage,StudentOtherAnswer,StudentOtherAnswerImage,\
    DaiMaAnswer,StudentDaiMaAnswer,QuestionScore,HomeworkScore

class KnowledgeLabelAdmin(object):
    list_display=['name','semester','lesson','teacher','unit_count','lesson_count','homework_count','question_count','create_user','create_time']
    search_fields=['name','lesson__name','teacher__name','teacher__id','id']
    list_filter=['name','semester','lesson__name','teacher__name','unit_count','lesson_count','homework_count','question_count','create_user__username','create_time']


class UnitAdmin(object):
    list_display=['num','name','semester','lesson','teacher','info','unit_type','parent_unit','create_time','update_time','create_user','id']
    search_fields=['name','lesson__name','teacher__name','create_user__username','id']
    list_filter=['num','name','semester','lesson__name','teacher__name','info','unit_type','parent_unit','create_time','update_time','create_user__username']


class LessonPeriodAdmin(object):
    list_display=['name','time','desc','schedule_lesson','create_time','update_time']
    search_fields=['name','desc','schedule_lesson__lesson__name','schedule_lesson__teacher__name','schedule_lesson__teacher__id','id']
    list_filter=['time','name','desc','schedule_lesson__lesson__name','schedule_lesson__teacher__name','schedule_lesson__semester','create_time','update_time']


class HomeworkAdmin(object):
    list_display=['lesson_period','title','describe','timeout','limit_time','user','question_counter','total_score','create_time','update_time']
    search_fields=['title','describe','user__username','user__name','lesson_period__name','lesson_period__schedule_lesson__lesson__name','id']
    list_filter=['lesson_period__schedule_lesson__teacher__name','lesson_period__schedule_lesson__lesson__name','lesson_period__schedule_lesson__semester','title','describe','timeout','limit_time','user__username','user__name','question_counter','total_score','create_time','update_time']

class QuestionAdmin(object):
    list_display=['question','homework','question_type','number','analysis','score','image_count','if_auto_correct','if_answer_update']
    search_fields=['question','analysis','id']
    list_filter=['homework__title','question_type','number','question','analysis','score','image_count','if_auto_correct','if_answer_update','homework__lesson_period__schedule_lesson__teacher__name','homework__lesson_period__schedule_lesson__lesson__name','homework__lesson_period__schedule_lesson__semester']


class QuestionImageAdmin(object):
    list_display=['question','number','image','create_time','update_time']
    search_fields=['question__question','question__analysis','id']
    list_filter=['number','question__homework__title','question__question_type','question__number','question__analysis','question__score','question__image_count','question__homework__lesson_period__schedule_lesson__teacher__name','question__homework__lesson_period__schedule_lesson__lesson__name','question__homework__lesson_period__schedule_lesson__semester']

class DaiMaFileAdmin(object):
    list_display=['question','daima_type','name','create_time','update_time','id']
    search_fields=['name','id','question__question','question__analysis','question__score','question__id']
    list_filter=['question__question','question__analysis','daima_type','name','create_time','update_time']

class ChoiceAdmin(object):
    list_display=['question','choice','content','create_time','update_time','id']
    search_fields=['content','question__question','question__analysis','question__id']
    list_filter=['question__question','question__analysis','choice','content','create_time','update_time']

class ChoiceTrueAnswerAdmin(object):
    list_display=['choice','question','create_time','update_time','id']
    search_fields=['choice__content','question__question','question__analysis','question__id']
    list_filter=['choice__choice','choice__content','question__question','question__analysis','create_time','update_time']

class StudentChoiceAnswerAdmin(object):
    list_display=['student','choice','question','create_time','update_time','id']
    search_fields=['student__name','student__id','choice__content','question__question','question__analysis','question__id']
    list_filter=['student__name','choice__content','choice__choice','question__question','question__analysis','create_time','update_time']

class PanDuanTrueAnswerAdmin(object):
    list_display=['question','answer','create_time','update_time','id']
    search_fields=['question__question','question__analysis','question__id']
    list_filter=['question__question','question__analysis','answer','create_time','update_time']

class StudentPanDuanAnswerAdmin(object):
    list_display=['student','question','answer','create_time','update_time','id']
    search_fields=['student__name','student__id','question__question','question__analysis','question__id']
    list_filter=['student__name','question__question','question__analysis','answer','create_time','update_time']

class TianKongBlankAdmin(object):
    list_display=['question','number','score','if_other_answer','create_time','update_time']
    search_fields=['question__question','question__analysis','question__id']
    list_filter=['question__question','question__analysis','number','score','if_other_answer','create_time','update_time']

class TianKongTrueAnswerAdmin(object):
    list_display=['answer','blank','create_time','update_time','id']
    search_fields=['blank__question__question','blank__question__analysis','answer']
    list_filter=['answer','blank__question__question','blank__question__analysis','create_time','update_time']

class TianKongOtherAnswerAdmin(object):
    list_display=['blank','other_answer','create_time','update_time','id']
    search_fields = ['blank__question__question', 'blank__question__analysis', 'other_answer']
    list_filter = ['other_answer', 'blank__question__question', 'blank__question__analysis', 'create_time', 'update_time']

class StudentTianKongAnswerAdmin(object):
    list_display=['student','answer','blank','create_time','update_time','id']
    search_fields=['student__name','student__id','blank__question__question','blank__question__analysis','answer']
    list_filter=['student__name','answer','blank__question__question','blank__question__analysis','create_time','update_time']

class JianDaAnswerAdmin(object):
    list_display=['answer','question','create_time','update_time','id']
    search_fields=['answer','question__question','question__analysis','question__id']
    list_filter=['answer','question__question','question__analysis','create_time','update_time']

class StudentJianDaAnswerAdmin(object):
    list_display=['question','answer','student','if_auto_submit','create_time','update_time','id']
    search_fields=['question__question','question__analysis','question__id','answer','student__name','student__id']
    list_filter=['question__question','question__analysis','answer','student__name','if_auto_submit','create_time','update_time']

class OtherAnswerAdmin(object):
    list_display=['text_answer','question','create_time','update_time','image_count','id']
    search_fields=['text_answer','question__question','question__analysis','question__id']
    list_filter=['text_answer','question__question','question__analysis','create_time','update_time','image_count']

class OtherAnswerImageAdmin(object):
    list_display=['other_answer','number','image','create_time','update_time','id']
    search_fields=['other_answer__question__question','other_answer__question__analysis','other_answer__question__id','other_answer__text_answer']
    list_filter=['number','other_answer__question__question','other_answer__question__analysis','other_answer__text_answer','create_time','update_time']

class StudentOtherAnswerAdmin(object):
    list_display=['student','text_answer','question','create_time','update_time','image_count','id']
    search_fields=['student__name','student__id','text_answer','question__question','question__analysis','question__id']
    list_filter=['student__name','text_answer','question__question','question__analysis','create_time','update_time','image_count']

class StudentOtherAnswerImageAdmin(object):
    list_display=['student_other_answer','number','image','create_time','update_time','id']
    search_fields=['student_other_answer__student__name','student_other_answer__student__id',\
                   'student_other_answer__text_answer','student_other_answer__question__question',\
                   'student_other_answer__question__id','student_other_answer__question__analysis']
    list_filter=['student_other_answer__student__name','student_other_answer__text_answer',\
                 'student_other_answer__question__question','student_other_answer__question__analysis',\
                 'number','create_time','update_time']


class DaiMaAnswerAdmin(object):
    list_display=['daima_file','daima_type','answer','create_time','update_time','id']
    search_fields=['answer','daima_file__question__question','daima_file__question__analysis','daima_file__question__id']
    list_filter=['daima_file__question__question','daima_file__question__analysis','daima_type','answer','create_time','update_time']

class StudentDaiMaAnswerAdmin(object):
    list_display=['daima_file','daima_type','answer','student','if_auto_submit','create_time','update_time','id']
    search_fields=['daima_file__question__question','daima_file__question__analysis','daima_file__question__id','answer','student__name','student__id']
    list_filter=['daima_type','daima_file__question__question','daima_file__question__analysis','answer','student__name','student__id','if_auto_submit','create_time','update_time']

class QuestionScoreAdmin(object):
    list_display=['question','student','score','create_time','update_time','if_no_answer','id']
    search_fields=['student__name','student__id','question__question','question__analysis','question__id']
    list_filter=['question__question','question__analysis','student__name','score','create_time','update_time','if_no_answer']

class HomeworkScoreAdmin(object):
    list_display=['homework','student','total_score','if_submit','create_time','update_time','if_no_answer','id']
    search_fields=['homework__title','homework__describe','student__name','student__id','homework__id']
    list_filter=['homework__title','homework__describe','student__name','total_score','if_submit','create_time','update_time','if_no_answer']

xadmin.site.register(KnowledgeLabel,KnowledgeLabelAdmin)
xadmin.site.register(Unit,UnitAdmin)
xadmin.site.register(LessonPeriod,LessonPeriodAdmin)
xadmin.site.register(Homework,HomeworkAdmin)
xadmin.site.register(Question,QuestionAdmin)
xadmin.site.register(QuestionImage,QuestionImageAdmin)
xadmin.site.register(DaiMaFile,DaiMaFileAdmin)
xadmin.site.register(Choice,ChoiceAdmin)
xadmin.site.register(ChoiceTrueAnswer,ChoiceTrueAnswerAdmin)
xadmin.site.register(StudentChoiceAnswer,StudentChoiceAnswerAdmin)
xadmin.site.register(PanDuanTrueAnswer,PanDuanTrueAnswerAdmin)
xadmin.site.register(StudentPanDuanAnswer,StudentPanDuanAnswerAdmin)
xadmin.site.register(TianKongBlank,TianKongBlankAdmin)
xadmin.site.register(TianKongTrueAnswer,TianKongTrueAnswerAdmin)
xadmin.site.register(TianKongOtherAnswer,TianKongOtherAnswerAdmin)
xadmin.site.register(StudentTianKongAnswer,StudentTianKongAnswerAdmin)
xadmin.site.register(JianDaAnswer,JianDaAnswerAdmin)
xadmin.site.register(StudentJianDaAnswer,StudentJianDaAnswerAdmin)
xadmin.site.register(OtherAnswer,OtherAnswerAdmin)
xadmin.site.register(OtherAnswerImage,OtherAnswerImageAdmin)
xadmin.site.register(StudentOtherAnswer,StudentOtherAnswerAdmin)
xadmin.site.register(StudentOtherAnswerImage,StudentOtherAnswerImageAdmin)
xadmin.site.register(DaiMaAnswer,DaiMaAnswerAdmin)
xadmin.site.register(StudentDaiMaAnswer,StudentDaiMaAnswerAdmin)
xadmin.site.register(QuestionScore,QuestionScoreAdmin)
xadmin.site.register(HomeworkScore,HomeworkScoreAdmin)
