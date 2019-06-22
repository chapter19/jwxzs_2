from django.db import models

from lessons.models import ScheduleLesson,Lesson
from users.models import UserProfile,Teacher,Student
from disks.models import File
from semesters.models import Semester


from datetime import datetime


class KnowledgeLabel(models.Model):
    name = models.CharField(max_length=50, verbose_name='知识点标签名', default='')
    semester=models.ForeignKey(Semester,verbose_name='学期',related_name='knowledge_label')
    lesson=models.ForeignKey(Lesson,verbose_name='课程',related_name='knowledge_label')
    teacher=models.ForeignKey(Teacher,verbose_name='教师',related_name='knowledge_label')
    unit_count=models.IntegerField(default=0,verbose_name='所包含知识点的章节数')
    lesson_count=models.IntegerField(default=0,verbose_name='所包含知识点的课时')
    homework_count=models.IntegerField(default=0,verbose_name='所包含知识点的作业')
    question_count=models.IntegerField(default=0,verbose_name='所包含知识点的题目')
    create_user=models.ForeignKey(UserProfile,verbose_name='创建人',related_name='my_create_knowledge_label')
    create_time=models.DateTimeField(auto_now_add=True,verbose_name='创建时间')
    class Meta:
        verbose_name='知识点标签'
        verbose_name_plural=verbose_name
        unique_together=('name','semester','lesson','teacher')
    def __str__(self):
        return self.name


class Unit(models.Model):
    num = models.IntegerField(verbose_name='第几章节', default=1)
    name=models.CharField(max_length=50,verbose_name='章节名')
    semester = models.ForeignKey(Semester, verbose_name='学期', related_name='unit')
    lesson = models.ForeignKey(Lesson, verbose_name='课程', related_name='unit')
    teacher = models.ForeignKey(Teacher, verbose_name='教师', related_name='unit')
    info=models.CharField(max_length=200,verbose_name='简介',blank=True,null=True,help_text='简介')
    unit_type=models.IntegerField(choices=((1,'章'),(2,'节'),(3,'子节')),verbose_name='章节类别')
    parent_unit=models.ForeignKey('self',null=True,blank=True,verbose_name='父章节',related_name='sub_unit')
    lesson_file = models.ManyToManyField(File, verbose_name='章节课件', related_name='unit',blank=True)
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time=models.DateTimeField(auto_now=True,verbose_name='修改时间')
    create_user=models.ForeignKey(UserProfile,verbose_name='创建人',related_name='my_create_unit')
    knowledge_labels = models.ManyToManyField(KnowledgeLabel, verbose_name='知识点标签', related_name='unit',blank=True)
    class Meta:
        verbose_name='章节'
        verbose_name_plural=verbose_name
        unique_together=('num','semester','lesson','teacher','unit_type')
    def __str__(self):
        return self.name


class LessonPeriod(models.Model):
    time=models.DateField(verbose_name='上课时间',auto_now_add=True)
    name=models.CharField(verbose_name='课时名',max_length=50,blank=True,null=True)
    desc=models.TextField(verbose_name='课时说明',blank=True,null=True)
    lesson_file=models.ManyToManyField(File,verbose_name='课时课件',related_name='lesson_period',blank=True)
    unit=models.ManyToManyField(Unit,related_name='lesson_period',verbose_name='章节',blank=True)
    schedule_lesson=models.ForeignKey(ScheduleLesson,verbose_name='课程表课程班级',related_name='lesson_period')
    create_time = models.DateTimeField(verbose_name='创建时间',default=datetime.now)
    update_time = models.DateTimeField(auto_now=True, verbose_name='修改时间')
    class Meta:
        verbose_name='课时'
        verbose_name_plural=verbose_name
    def __str__(self):
        return self.name


class Homework(models.Model):
    lesson_period=models.ForeignKey(LessonPeriod,verbose_name='课时',related_name='homework')
    title=models.CharField(verbose_name='标题',max_length=50,default='')
    describe=models.TextField(verbose_name='作业描述',default='')
    timeout=models.IntegerField(verbose_name='完成时间限制（分钟）',blank=True,null=True)
    limit_time=models.DateTimeField(verbose_name='提交时间限制',default=datetime.now)
    file=models.ManyToManyField(File,verbose_name='作业文件',related_name='homework')
    user=models.ForeignKey(UserProfile,verbose_name='作业创建者',related_name='my_created_homework')
    question_counter=models.IntegerField(default=0,verbose_name='题目量（题）')
    total_score=models.FloatField(default=0.0,verbose_name='总分')
    create_time = models.DateTimeField(verbose_name='创建时间',default=datetime.now)
    update_time = models.DateTimeField(auto_now=True, verbose_name='修改时间')
    class Meta:
        verbose_name='作业'
        verbose_name_plural=verbose_name
        unique_together=('lesson_period','title')
    def __str__(self):
        return self.title


class Question(models.Model):
    homework = models.ForeignKey(Homework, verbose_name='作业')
    knowledge_labels=models.ManyToManyField(KnowledgeLabel,verbose_name='知识点标签',related_name='question')
    question_type=models.CharField(choices=(('DanXuan','单选题'),('PanDuan','判断题'),('DuoXuan','多选题'),('TianKong','填空题'),('JianDa','简答题'),('DaiMa','代码题'),('QiTa','其他题')),verbose_name='题目类型',max_length=12)
    number=models.IntegerField(default=1,verbose_name='编号')
    question=models.TextField(verbose_name='题目',default='')
    analysis=models.TextField(verbose_name='解析',blank=True,null=True)
    score=models.FloatField(default=0.0,verbose_name='分值')
    image_count=models.IntegerField(default=0,verbose_name='图片数量')
    if_auto_correct=models.BooleanField(default=False,verbose_name='是否自动批改')
    if_answer_update=models.BooleanField(default=False,verbose_name='学生是否可以修改答案')
    class Meta:
        verbose_name='题目'
        verbose_name_plural=verbose_name
        unique_together=('homework','number')
    def __str__(self):
        return self.question


class QuestionImage(models.Model):
    number=models.IntegerField(default=1,verbose_name='编号')
    image=models.ImageField(upload_to='question/%Y/%m/%d/',verbose_name='图片')
    question=models.ForeignKey(Question,verbose_name='题目',related_name='image')
    create_time = models.DateTimeField(verbose_name='创建时间', default=datetime.now)
    update_time = models.DateTimeField(auto_now=True, verbose_name='修改时间')
    class Meta:
        verbose_name='题目图片'
        verbose_name_plural=verbose_name
        unique_together=('question','number')
        ordering=('number',)
    def __str__(self):
        return self.question.question


class DaiMaFile(models.Model):
    question=models.ForeignKey(Question,verbose_name='题目',help_text='题目')
    daima_type = models.CharField(max_length=12,choices=(
    ('python','Python'), ('c', 'C'),('cpp','C++'),('php', 'Php'), ('java', 'Java'), ('csharp', 'C#'),('r','R'),
    ('javascript', 'JavaScript'), ('Html', 'Html'), ('css', 'Css'), ('vbscript', 'VB'),('jsp','jsp'),('sql','SQL'),('xml','XML'),('golang','Go'),('mysql','MySQL'),('sh','shell'),('不限','不限')),verbose_name='编程语言',help_text='编程语言')
    name=models.CharField(verbose_name='代码文件名',max_length=50,help_text='代码文件名')
    create_time = models.DateTimeField(verbose_name='创建时间', default=datetime.now,help_text='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='修改时间',help_text='修改时间')
    class Meta:
        verbose_name='代码题代码文件'
        verbose_name_plural=verbose_name
        unique_together=('name','question')
    def __str__(self):
        return self.name


class Choice(models.Model):
    question = models.ForeignKey(Question, verbose_name='题目', related_name='choice')
    choice=models.CharField(max_length=2,choices=(('A','A'),('B','B'),('C','C'),('D','D'),('E','E'),('F','F'),('G','G'),('H','H'),('I','I'),('J','J'),('K','K')),default='A',verbose_name='选项')
    content=models.CharField(max_length=100,verbose_name='选项内容',default='')
    create_time = models.DateTimeField(verbose_name='创建时间', default=datetime.now)
    update_time = models.DateTimeField(auto_now=True, verbose_name='修改时间')
    class Meta:
        verbose_name='选项'
        verbose_name_plural=verbose_name
        unique_together=('question','choice')
        ordering = ('choice',)
    def __str__(self):
        return self.question.question


class ChoiceTrueAnswer(models.Model):
    choice=models.ForeignKey(Choice,verbose_name='选项',related_name='choice_true_answer')
    question=models.ForeignKey(Question,verbose_name='问题',related_name='choice_true_answer')
    create_time = models.DateTimeField(verbose_name='创建时间', default=datetime.now)
    update_time = models.DateTimeField(auto_now=True, verbose_name='修改时间')
    class Meta:
        verbose_name='选择题正确答案'
        verbose_name_plural=verbose_name
        ordering = ('choice',)
    def __str__(self):
        return self.choice


class StudentChoiceAnswer(models.Model):
    student = models.ForeignKey(Student, verbose_name='学生', related_name='my_choice_answer')
    choice = models.ForeignKey(Choice, verbose_name='选项', related_name='student_answer')
    question = models.ForeignKey(Question, verbose_name='问题', related_name='danxuan_true_answer')
    create_time = models.DateTimeField(verbose_name='创建时间', default=datetime.now)
    update_time = models.DateTimeField(auto_now=True, verbose_name='修改时间')
    class Meta:
        verbose_name = '选择题学生答案'
        verbose_name_plural = verbose_name
        ordering = ('choice',)
    def __str__(self):
        return self.choice


class PanDuanTrueAnswer(models.Model):
    question=models.OneToOneField(Question,verbose_name='题目',related_name='panduan_true_answer')
    answer=models.BooleanField(default=False,verbose_name='正确与否（答案）')
    create_time = models.DateTimeField(verbose_name='创建时间', default=datetime.now)
    update_time = models.DateTimeField(auto_now=True, verbose_name='修改时间')
    class Meta:
        verbose_name='判断题正确答案'
        verbose_name_plural=verbose_name
    def __str__(self):
        return self.question.question

class StudentPanDuanAnswer(models.Model):
    student=models.ForeignKey(Student,verbose_name='学生用户',related_name='student_panduan_answer')
    question = models.ForeignKey(Question, verbose_name='题目', related_name='student_panduan_answer')
    answer = models.BooleanField(verbose_name='正确与否（答案）',default=False)
    create_time = models.DateTimeField(verbose_name='创建时间', default=datetime.now)
    update_time = models.DateTimeField(auto_now=True, verbose_name='修改时间')
    class Meta:
        verbose_name = '判断题学生答案'
        verbose_name_plural = verbose_name
        unique_together=('student','question')
    def __str__(self):
        return self.question.question

# class

class TianKongBlank(models.Model):
    question=models.ForeignKey(Question,verbose_name='题目',related_name='tiankong_blank')
    number=models.IntegerField(default=1,verbose_name='编号')
    score=models.FloatField(default=0.5,verbose_name='该空的分值')
    if_other_answer=models.BooleanField(default=False,verbose_name='是否有其他答案')
    create_time = models.DateTimeField(verbose_name='创建时间', default=datetime.now)
    update_time = models.DateTimeField(auto_now=True, verbose_name='修改时间')
    class Meta:
        verbose_name='填空题空'
        verbose_name_plural=verbose_name
        unique_together=('question','number')
        ordering=('number',)
    def __str__(self):
        return self.question.question


class TianKongTrueAnswer(models.Model):
    answer=models.CharField(max_length=50,verbose_name='答案')
    blank=models.OneToOneField(TianKongBlank,related_name='tiankong_true_answer')
    create_time = models.DateTimeField(verbose_name='创建时间', default=datetime.now)
    update_time = models.DateTimeField(auto_now=True, verbose_name='修改时间')
    class Meta:
        verbose_name='填空题空正确答案'
        verbose_name_plural=verbose_name
    def __str__(self):
        return self.answer


class TianKongOtherAnswer(models.Model):
    blank=models.ForeignKey(TianKongBlank,verbose_name='填空',related_name='tiankong_other_answer')
    other_answer=models.CharField(max_length=50,verbose_name='其他答案')
    create_time = models.DateTimeField(verbose_name='创建时间', default=datetime.now)
    update_time = models.DateTimeField(auto_now=True, verbose_name='修改时间')
    class Meta:
        verbose_name='填空题空其他答案'
        verbose_name_plural=verbose_name
        unique_together=('other_answer','blank')
    def __str__(self):
        return self.other_answer


class StudentTianKongAnswer(models.Model):
    student = models.ForeignKey(Student, verbose_name='学生', related_name='student_tiankong_answer')
    answer=models.CharField(max_length=50,verbose_name='答案')
    blank=models.ForeignKey(TianKongBlank,related_name='student_tiankong_answer',verbose_name='填空题空')
    create_time = models.DateTimeField(verbose_name='创建时间', default=datetime.now)
    update_time = models.DateTimeField(auto_now=True, verbose_name='修改时间')
    class Meta:
        verbose_name='填空题空学生答案'
        verbose_name_plural=verbose_name
        unique_together=('student','blank')
    def __str__(self):
        return self.answer


class JianDaAnswer(models.Model):
    answer = models.TextField(verbose_name='文本答案', blank=True, null=True)
    question = models.OneToOneField(Question, verbose_name='题目', related_name='jianda_answer')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='修改时间')
    class Meta:
        verbose_name='简答题参考答案'
        verbose_name_plural=verbose_name
    def __str__(self):
        return self.question.question


class StudentJianDaAnswer(models.Model):
    question=models.ForeignKey(Question,verbose_name='题目',related_name='student_jianda_answer')
    answer = models.TextField(verbose_name='文本答案', blank=True, null=True)
    student = models.ForeignKey(Student, verbose_name='学生', related_name='student_jianda_answer')
    if_auto_submit = models.BooleanField(default=False, verbose_name='是否自动提交')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='修改时间')
    class Meta:
        verbose_name='学生简答题答案'
        verbose_name_plural=verbose_name
    def __str__(self):
        return self.question.question


class OtherAnswer(models.Model):
    text_answer = models.TextField(verbose_name='文本答案', blank=True, null=True)
    question = models.OneToOneField(Question, verbose_name='题目', related_name='other_answer')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='修改时间')
    file = models.ManyToManyField(File, verbose_name='文件', related_name='other_answer')
    image_count=models.IntegerField(default=0,verbose_name='其他题答案照片数')
    class Meta:
        verbose_name = '其他题参考答案'
        verbose_name_plural = verbose_name
    def __str__(self):
        return self.question.question


class OtherAnswerImage(models.Model):
    number = models.IntegerField(default=1, verbose_name='编号')
    other_answer=models.ForeignKey(OtherAnswer,verbose_name='其他题答案',related_name='other_answer_image')
    image=models.ImageField(upload_to='student_other_answer_imgs/%Y/%m/%d/',verbose_name='图片')
    create_time = models.DateTimeField(verbose_name='创建时间', default=datetime.now)
    update_time = models.DateTimeField(auto_now=True, verbose_name='修改时间')
    class Meta:
        verbose_name='其他题参考答案图片'
        verbose_name_plural=verbose_name
        unique_together = ('number', 'other_answer')
        ordering=('number',)
    def __str__(self):
        return self.other_answer.text_answer


class StudentOtherAnswer(models.Model):
    text_answer = models.TextField(verbose_name='文本答案', blank=True, null=True)
    question = models.ForeignKey(Question, verbose_name='题目', related_name='student_other_answer')
    student = models.ForeignKey(Student, verbose_name='学生', related_name='student_other_answer')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='修改时间')
    file=models.ManyToManyField(File,verbose_name='文件',related_name='student_other_answer')
    image_count=models.IntegerField(default=0,verbose_name='图片数量')
    class Meta:
        verbose_name='学生其他题答案'
        verbose_name_plural=verbose_name
        unique_together=('question','student')
    def __str__(self):
        return self.question.question


class StudentOtherAnswerImage(models.Model):
    number=models.IntegerField(default=1,verbose_name='编号')
    student_other_answer=models.ForeignKey(StudentOtherAnswer,verbose_name='学生其他题答案',related_name='student_other_answer_image')
    image=models.ImageField(upload_to='student_other_answer_imgs/%Y/%m/%d/',verbose_name='图片')
    create_time = models.DateTimeField(verbose_name='创建时间', default=datetime.now)
    update_time = models.DateTimeField(auto_now=True, verbose_name='修改时间')
    class Meta:
        verbose_name='学生其他题答案图片'
        verbose_name_plural=verbose_name
        unique_together=('number','student_other_answer')
    def __str__(self):
        return self.student_other_answer.student.name


class DaiMaAnswer(models.Model):
    daima_type = models.CharField(max_length=12, choices=(
        ('python', 'Python'), ('c_cpp', 'C'), ('c_cpp', 'C++'), ('php', 'Php'), ('java', 'Java'), ('csharp', 'C#'),
        ('r', 'R'),
        ('javascript', 'JavaScript'), ('html', 'Html'), ('css', 'Css'), ('vbscript', 'VB'), ('jsp', 'jsp'),
        ('sql', 'SQL'), ('xml', 'XML'), ('golang', 'Go'), ('mysql', 'MySQL'), ('sh', 'shell'), ('其他', '其他')),verbose_name='编程语言')
    daima_file = models.ForeignKey(DaiMaFile, verbose_name='对应代码文件', related_name='daima_answer')
    answer = models.TextField(verbose_name='代码答案')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='修改时间')
    class Meta:
        verbose_name='代码参考答案'
        verbose_name_plural=verbose_name
    def __str__(self):
        return self.daima_file.name


class StudentDaiMaAnswer(models.Model):
    daima_type = models.CharField(max_length=12,choices=(
        ('python', 'Python'), ('c', 'C'), ('cpp', 'C++'), ('php', 'Php'), ('java', 'Java'), ('csharp', 'C#'),
        ('r', 'R'),
        ('javascript', 'JavaScript'), ('Html', 'Html'), ('css', 'Css'), ('vbscript', 'VB'), ('jsp', 'jsp'),
        ('sql', 'SQL'), ('xml', 'XML'), ('golang', 'Go'), ('mysql', 'MySQL'), ('sh', 'shell'), ('其他', '其他')),
        verbose_name='编程语言')
    daima_file=models.ForeignKey(DaiMaFile,verbose_name='对应代码文件',related_name='student_daima_answer')
    answer=models.TextField(verbose_name='代码答案',blank=True,null=True)
    student=models.ForeignKey(Student,verbose_name='学生',related_name='student_daima_answer')
    if_auto_submit=models.BooleanField(default=False,verbose_name='是否自动提交')
    create_time=models.DateTimeField(auto_now_add=True,verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='修改时间')
    class Meta:
        verbose_name='学生代码答案'
        verbose_name_plural=verbose_name
    def __str__(self):
        return self.student.name


class QuestionScore(models.Model):
    student=models.ForeignKey(Student,verbose_name='学生',related_name='question_score')
    question=models.ForeignKey(Question,verbose_name='题目',related_name='question_score')
    score=models.FloatField(default=0.0,verbose_name='成绩')
    create_time = models.DateTimeField(verbose_name='创建时间', default=datetime.now)
    update_time = models.DateTimeField(auto_now=True, verbose_name='修改时间')
    if_no_answer=models.BooleanField(default=False,verbose_name='是否未答题',help_text='是否未答题')
    class Meta:
        verbose_name='题目得分'
        verbose_name_plural=verbose_name
        unique_together=('student','question')
    def __str__(self):
        return self.student.name


class HomeworkScore(models.Model):
    homework=models.ForeignKey(Homework,verbose_name='作业',related_name='student_homework_score')
    student = models.ForeignKey(Student, verbose_name='学生', related_name='student_homework_score')
    total_score=models.FloatField(default=0.0,verbose_name='总得分')
    if_submit=models.BooleanField(default=False,verbose_name='是否提交作业')
    create_time = models.DateTimeField(verbose_name='创建时间', default=datetime.now)
    update_time = models.DateTimeField(auto_now=True, verbose_name='修改时间')
    if_no_answer = models.BooleanField(default=False, verbose_name='是否未答题', help_text='是否未答题')
    class Meta:
        verbose_name='单次作业总得分'
        verbose_name_plural=verbose_name
        unique_together=('student','homework')
    def __str__(self):
        return self.student.name











