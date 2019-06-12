from django.db import models
from users.models import UserProfile,Student,Teacher
from semesters.models import Semester
from lessons.models import Lesson

# Create your models here.

class PingJiaoTeacher(models.Model):
    student=models.ForeignKey(Student,related_name='my_pingjiao_teacher',verbose_name='学生')
    teacher=models.ForeignKey(Teacher,related_name='who_pingjiao_me',verbose_name='教师')
    lesson_name=models.CharField(max_length=100,verbose_name='课程名',blank=True,null=True)
    semester=models.ForeignKey(Semester,verbose_name='学期',related_name='pingjiao_teacher')
    score=models.FloatField(verbose_name='评分',blank=True,null=True)
    grade=models.CharField(choices=(('groupA','优秀'),('groupB','良好'),('groupC','中等'),('groupD','合格')),max_length=6,verbose_name='等级',blank=True,null=True)
    code=models.CharField(max_length=50,verbose_name='参数',default='')
    class Meta:
        verbose_name='评教老师'
        verbose_name_plural=verbose_name
        unique_together=('student','lesson_name','semester',)
    def __str__(self):
        return self.teacher.name

class LessonLabels(models.Model):
    lesson=models.ForeignKey(Lesson,related_name='my_label',verbose_name='课程')
    label=models.CharField(max_length=20,verbose_name='分词标签',help_text='分词标签',default='')
    add_time=models.DateTimeField(auto_now_add=True,verbose_name='添加时间')
    class Meta:
        verbose_name='课程标签'
        verbose_name_plural=verbose_name
        unique_together=('lesson','label')
    def __str__(self):
        return self.label


class StepOneLessonTeacher(models.Model):
    lesson=models.ForeignKey(Lesson,related_name='step_one_lesson_teacher',verbose_name='课程')
    teacher=models.ForeignKey(Teacher,related_name='my_step_one_lesson',verbose_name='教师')
    semester=models.ForeignKey(Semester,related_name='step_one_lesson_teacher',verbose_name='学期')
    post_code=models.CharField(max_length=100,verbose_name='表单码',help_text='表单码',default='')
    add_time = models.DateTimeField(auto_now_add=True, verbose_name='添加时间')
    class Meta:
        verbose_name='预选阶段课程教师'
        verbose_name_plural=verbose_name
        unique_together=('lesson','semester','teacher')
    def __str__(self):
        return '{0} {1}'.format(self.teacher.name,self.lesson.name)



class MyXuanKe(models.Model):
    student=models.ForeignKey(Student,related_name='my_xuanke',verbose_name='学生')
    # lesson=models.ForeignKey(Lesson,related_name='who_xuanke_me',verbose_name='课程')
    # teacher=models.ForeignKey(Teacher,related_name='who_xuan_me',verbose_name='教师')
    lesson_type=models.CharField(max_length=20,verbose_name='课程性质',default='专业主干')
    lesson_teacher=models.ForeignKey(StepOneLessonTeacher,related_name='who_xuanke_me',verbose_name='课程教师')
    point=models.IntegerField(verbose_name='选点',default=0)
    delete_post_code=models.CharField(max_length=100,verbose_name='删除表单码',default='')
    # can_delete = models.BooleanField(default=True, verbose_name='可删')
    # semester=models.ForeignKey(Semester,related_name='xuanke',verbose_name='选课')
    class Meta:
        verbose_name='选课'
        verbose_name_plural=verbose_name
        unique_together=('student','lesson_teacher')
    def __str__(self):
        return self.student.name










