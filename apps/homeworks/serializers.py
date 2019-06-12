# -*- coding:utf-8 -*-

from rest_framework import serializers
from datetime import datetime, timedelta

from .models import Unit, File, KnowledgeLabel, LessonPeriod, Homework, Question, QuestionImage, QuestionScore, \
    Choice, StudentChoiceAnswer, HomeworkScore, ChoiceTrueAnswer, PanDuanTrueAnswer, StudentPanDuanAnswer,TianKongBlank,\
    TianKongTrueAnswer,TianKongOtherAnswer,StudentTianKongAnswer,JianDaAnswer,StudentJianDaAnswer,OtherAnswerImage,OtherAnswer,\
    StudentOtherAnswer,StudentOtherAnswerImage,DaiMaFile,DaiMaAnswer,StudentDaiMaAnswer
from users.serializer import UserSerializer
from users.models import Teacher, UserProfile
from semesters.models import Semester
from lessons.models import Lesson, ScheduleLesson
from disks.serializers import FileListSerializer
from scores.models import Score


class KnowledgeLabelListSerializer(serializers.ModelSerializer):
    class Meta:
        model = KnowledgeLabel
        fields = '__all__'


class KnowledgeLabelCreateSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    user_id = serializers.HiddenField(default=serializers.CurrentUserDefault())
    semester_post_code = serializers.CharField(required=True, help_text='学期表单码', write_only=True, label='学期表单码')

    # lesson_id=serializers.IntegerField(required=True,help_text='课程id',label='课程id')
    class Meta:
        model = KnowledgeLabel
        fields = ['name', 'lesson_id', 'id', 'semester_post_code', 'user_id', 'lesson']

    def create(self, validated_data):
        user_id = validated_data.get('user_id')
        teacher = Teacher.objects.filter(user_id=user_id)
        if teacher:
            teacher = teacher[0]
            semester_post_code = validated_data.get('semester_post_code')
            semester = Semester.objects.filter(post_code=semester_post_code)
            if semester:
                semester = semester[0]
                lesson = validated_data.get('lesson')
                if lesson:
                    schedule_lesson = ScheduleLesson.objects.filter(semester=semester_post_code, teacher=teacher,
                                                                    lesson=lesson)
                    if schedule_lesson:
                        name = validated_data.get('name')
                        try:
                            knowledge_label = KnowledgeLabel.objects.create(semester=semester, lesson=lesson,
                                                                            teacher=teacher, name=name)
                            return knowledge_label
                        except:
                            raise serializers.ValidationError({'detail': '该知识点标签已存在！请勿重复创建'})
                    else:
                        raise serializers.ValidationError({'detail': '你该学期没有开设该课程，不能创建该课程的知识点！'})
                else:
                    raise serializers.ValidationError({'detail': '课程不存在！'})
            else:
                raise serializers.ValidationError({'detail': '学期不存在！'})
        else:
            raise serializers.ValidationError({'detail': '你不是教师，不能创建知识点标签！'})


class UnitList3Serializers(serializers.ModelSerializer):
    lesson_file = FileListSerializer(many=True)
    update_time = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%s')
    create_time = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%s')

    class Meta:
        model = Unit
        fields = ['num', 'name', 'semester', 'lesson', 'teacher', 'info', 'unit_type', 'parent_unit', 'create_time',
                  'update_time', 'lesson_file', 'create_user']


class UnitList2Serializers(serializers.ModelSerializer):
    sub_unit = UnitList3Serializers(many=True)
    lesson_file = FileListSerializer(many=True)
    update_time = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%s')
    create_time = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%s')

    class Meta:
        model = Unit
        fields = ['num', 'name', 'semester', 'lesson', 'teacher', 'info', 'unit_type', 'parent_unit', 'create_time',
                  'update_time', 'lesson_file', 'create_user']


class UnitList1Serializers(serializers.ModelSerializer):
    sub_unit = UnitList2Serializers(many=True)
    lesson_file = FileListSerializer(many=True)
    update_time = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%s')
    create_time = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%s')

    class Meta:
        model = Unit
        fields = ['num', 'name', 'semester', 'lesson', 'teacher', 'info', 'unit_type', 'parent_unit', 'create_time',
                  'update_time', 'lesson_file', 'create_user']


class UnitCreateSerializers(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    user_id = serializers.HiddenField(default=serializers.CurrentUserDefault())
    semester_post_code = serializers.CharField(help_text='学期表单码', label='学期表单码', required=True, write_only=True)

    # lesson_file_id_list=serializers.ListField(child=serializers.UUIDField(),required=False,write_only=True,help_text='文件id列表',label='文件id列表')
    class Meta:
        model = Unit
        fields = ['num', 'name', 'semester_post_code', 'lesson', 'info', 'parent_unit', 'lesson_file', 'id', 'user_id',
                  'knowledge_labels']

    def create(self, validated_data):
        user_id = validated_data.get('user_id')
        teacher = Teacher.objects.filter(user_id=user_id)
        if teacher:
            teacher = teacher[0]
            lesson = validated_data.get('lesson')
            semester_post_code = validated_data.get('semester_post_code')
            semester = Semester.objects.filter(post_code=semester_post_code)
            if semester:
                semester = semester[0]
                schedule_lesson = ScheduleLesson.objects.filter(teacher=teacher, lesson=lesson,
                                                                semester=semester_post_code)
                if schedule_lesson:
                    parent_unit = validated_data.get('parent_unit')
                    if parent_unit:
                        unit_type = parent_unit + 1
                    else:
                        unit_type = 1
                    num = validated_data.get('num')
                    unit = Unit.objects.filter(teacher=teacher, lesson=lesson, semester=semester, unit_type=unit_type,
                                               num=num)
                    if unit:
                        raise serializers.ValidationError({'detail': '该文件已存在！'})
                    else:
                        unit = Unit(teacher=teacher, lesson=lesson, semester=semester, num=num, unit_type=unit_type)
                    if parent_unit:
                        unit.parent_unit = parent_unit
                    lesson_file = validated_data.get('lesson_file')
                    if lesson_file:
                        for file in lesson_file:
                            disk = file.disk
                            if disk.ower_id != user_id:
                                raise serializers.ValidationError({'detail': '这不是你的文件！不能添加'})
                            if disk.if_disable:
                                raise serializers.ValidationError({'detail': '你的网盘已被禁用！不能再使用'})
                            if disk.if_close:
                                raise serializers.ValidationError({'detail': '你的网盘已经关闭！先去开启再继续使用吧'})
                            if file.if_delete:
                                raise serializers.ValidationError({'detail': '该文件已被回收！不能选择'})
                            try:
                                unit.lesson_file.add(file)
                            except:
                                raise serializers.ValidationError({'detail': '该文件已添加！勿重复添加！'})
                    name = validated_data.get('name')
                    unit.name = name
                    info = validated_data.get('info')
                    unit.info = info
                    unit.create_user_id = user_id
                    knowledge_labels = validated_data.get('knowledge_labels')
                    for k_l in knowledge_labels:
                        if k_l.teacher != teacher:
                            raise serializers.ValidationError({"detail": "你不是该标签的老师，不能添加该知识点标签！"})
                        if k_l.lesson != lesson:
                            raise serializers.ValidationError({'detail': '该知识点标签不属于该课程！不能添加'})
                        if k_l.semester != semester:
                            raise serializers.ValidationError({'detail': '该知识点标签不属于该学期！不能添加'})
                        try:
                            unit.knowledge_labels.add(k_l)
                            k_l.unit_count += 1
                            k_l.save()
                        except:
                            raise serializers.ValidationError({'detail': '知识点标签重复！'})
                    try:
                        unit.save()
                    except:
                        raise serializers.ValidationError({'detail': '文件或知识点重复！创建大纲失败！'})
                    return unit
                else:
                    raise serializers.ValidationError({'detail': '你该学期未开设该课程！不能创建该课程大纲'})
            else:
                raise serializers.ValidationError({'detail': '学期不存在！'})
        else:
            raise serializers.ValidationError({'detail': '你不是教师！不能创建课程大纲'})


class UnitUpdateSerialiser(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    user_id = serializers.HiddenField(default=serializers.CurrentUserDefault())
    lesson_file_add_id_list = serializers.ListField(child=serializers.UUIDField(), required=False, allow_null=True,
                                                    write_only=True, help_text='新增的文件id列表', label='新增的文件id列表')
    knowledge_label_add_id_list = serializers.ListField(child=serializers.IntegerField(), required=False,
                                                        allow_null=True, write_only=True, help_text='新增的知识点标签id列表',
                                                        label='新增的知识点标签id列表')
    knowledge_label_remove_id_list = serializers.ListField(child=serializers.IntegerField(), required=False,
                                                           allow_null=True, write_only=True, help_text='删除的知识点标签id列表',
                                                           label='删除的知识点标签id列表')
    lesson_file_remove_id_list = serializers.ListField(child=serializers.UUIDField(), required=False, allow_null=True,
                                                       write_only=True, help_text='删除的文件id列表', label='删除的文件id列表')

    class Meta:
        model = Unit
        fields = ['num', 'name', 'info', 'lesson_file_remove_id_list', 'lesson_file_add_id_list', 'id', 'user_id',
                  'knowledge_label_remove_id_list', 'knowledge_label_add_id_list']

    def update(self, instance, validated_data):
        user_id = validated_data.get('user_id')
        if instance.create_user_id == user_id:
            pass
        else:
            raise serializers.ValidationError({'detail': '该章节不是你创建的！你不能修改该章节！'})
        try:
            instance.num = validated_data.get('num', instance.num)
            instance.save()
        except:
            raise serializers.ValidationError({'detail': '已存在该章节！'})
        instance.name = validated_data.get('name', instance.name)
        instance.info = validated_data.get('info', instance.info)
        lesson_file_remove_id_list = validated_data.get('lesson_file_remove_id_list')
        if lesson_file_remove_id_list:
            for fi_id in lesson_file_remove_id_list:
                file = File.objects.filter(id=fi_id)
                if file:
                    file = file[0]
                    try:
                        instance.lesson_file.remove(file)
                    except:
                        raise serializers.ValidationError({'detail': '课件不存在！不能删除！修改失败'})
                else:
                    raise serializers.ValidationError({'detail': '文件不存在！修改失败'})
        lesson_file_add_id_list = validated_data.get('lesson_file_add_id_list')
        if lesson_file_add_id_list:
            for fi_id in lesson_file_add_id_list:
                file = File.objects.filter(id=fi_id)
                if file:
                    file = file[0]
                    disk = file.disk
                    if disk.ower_id != user_id:
                        raise serializers.ValidationError({'detail': '这不是你的文件！不能添加'})
                    if disk.if_disable:
                        raise serializers.ValidationError({'detail': '你的网盘已被禁用！不能再使用'})
                    if disk.if_close:
                        raise serializers.ValidationError({'detail': '你的网盘已经关闭！先去开启再继续使用吧'})
                    if file.if_delete:
                        raise serializers.ValidationError({'detail': '该文件已被回收！不能选择'})
                    try:
                        instance.lesson_file.add(file)
                    except:
                        raise serializers.ValidationError('该文件已添加！')
                else:
                    raise serializers.ValidationError({'detail': '该文件不存在！添加课件失败！'})
        knowledge_label_remove_id_list = validated_data.get('knowledge_label_remove_id_list')
        if knowledge_label_remove_id_list:
            for id in knowledge_label_remove_id_list:
                lab = KnowledgeLabel.objects.filter(id=id)
                if lab:
                    lab = lab[0]
                    try:
                        instance.knowledge_labels.remove(lab)
                        lab.unit_count -= 1
                    except:
                        raise serializers.ValidationError({'detail': '未添加该标签！不能删除！'})
                else:
                    raise serializers.ValidationError({'detail': '知识点标签不存在！'})
        knowledge_label_add_id_list = validated_data.get('knowledge_label_add_id_list')
        if knowledge_label_add_id_list:
            for id in knowledge_label_add_id_list:
                k_l = KnowledgeLabel.objects.filter(id=id)
                if k_l:
                    k_l = k_l[0]
                    if k_l.teacher != instance.teacher:
                        raise serializers.ValidationError({"detail": "你不是该标签的老师，不能添加该知识点标签！"})
                    if k_l.lesson != instance.lesson:
                        raise serializers.ValidationError({'detail': '该知识点标签不属于该课程！不能添加'})
                    if k_l.semester != instance.semester:
                        raise serializers.ValidationError({'detail': '该知识点标签不属于该学期！不能添加'})
                    try:
                        instance.knowledge_labels.add(k_l)
                        k_l.unit_count += 1
                        k_l.save()
                    except:
                        raise serializers.ValidationError({'detail': '知识点标签重复！'})
                else:
                    raise serializers.ValidationError({'detail': '该知识点标签不存在！'})
        try:
            instance.save()
        except:
            raise serializers.ValidationError({'detail': '课件或知识点标签出错！'})
        return instance


class ScheduleLessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScheduleLesson
        fields = '__all__'


class LessonPeriodListSerializer(serializers.ModelSerializer):
    schedule_lesson = ScheduleLessonSerializer()
    lesson_file = FileListSerializer(many=True)

    class Meta:
        model = LessonPeriod
        fields = '__all__'


class LessonPeriodCreateSerializer(serializers.ModelSerializer):
    user_id = serializers.HiddenField(default=serializers.CurrentUserDefault())
    id = serializers.IntegerField(read_only=True)

    class Meta:
        model = LessonPeriod
        fields = ['name', 'desc', 'schedule_lesson', 'unit', 'lesson_file', 'user_id', 'id', 'time']

    def create(self, validated_data):
        user_id = validated_data.get('user_id')
        user = UserProfile.objects.get(id=user_id)
        if user.if_teacher:
            schedule_lesson = validated_data.get('schedule_lesson')
            if schedule_lesson.teacher == user.teacher:
                lesson_period = LessonPeriod(name=validated_data.get('name'), desc=validated_data.get('desc'),
                                             schedule_lesson=schedule_lesson)
                unit = validated_data.get('unit')
                if unit:
                    for u in unit:
                        if (u.semester.post_code == schedule_lesson.semester) and (u.teacher == user.teacher) and (
                                u.lesson == schedule_lesson.lesson):
                            try:
                                lesson_period.unit.add(u)
                            except:
                                raise serializers.ValidationError({'detail': '章节重复！创建失败'})
                        else:
                            raise serializers.ValidationError({'detail': '包含不是你创建的课程大纲！不能添加'})
                lesson_file = validated_data.get('lesson_file')
                if lesson_file:
                    for f in lesson_file:
                        disk = f.disk
                        if disk.ower != user:
                            raise serializers.ValidationError({'detail': '这不是你的文件！不能添加'})
                        if disk.if_disable:
                            raise serializers.ValidationError({'detail': '你的网盘已被禁用！不能再使用'})
                        if disk.if_close:
                            raise serializers.ValidationError({'detail': '你的网盘已经关闭！先去开启再继续使用吧'})
                        if f.if_delete:
                            raise serializers.ValidationError({'detail': '该文件已被回收！不能选择'})
                        try:
                            lesson_period.lesson_file.add(f)
                        except:
                            raise serializers.ValidationError({'detail': '文件重复！创建失败'})
                time = validated_data.get('time')
                lesson_period.time = time
                try:
                    lesson_period.save()
                except:
                    raise serializers.ValidationError({'detail': '文件或章节重复！创建失败！'})
                return lesson_period
            else:
                raise serializers.ValidationError({'detail': '你不是该课程班级的老师！不能创建课时！'})
        else:
            raise serializers.ValidationError({"detail": "你不是教师！不能创建课时！"})


class LessonPeriodUpdateSerializer(serializers.ModelSerializer):
    user_id = serializers.HiddenField(default=serializers.CurrentUserDefault())
    add_unit_id_list = serializers.ListField(child=serializers.IntegerField(), write_only=True, label='添加的章节id列表',
                                             help_text='添加的章节id列表', required=False, allow_null=True)
    delete_unit_id_list = serializers.ListField(child=serializers.IntegerField(), write_only=True, label='删除的章节id列表',
                                                help_text='删除的章节id列表', required=False, allow_null=True)
    add_lesson_file_id_list = serializers.ListField(child=serializers.UUIDField(), write_only=True, label='添加的的课件id列表',
                                                    help_text='添加的的课件id列表', required=False, allow_null=True)
    delete_lesson_file_id_list = serializers.ListField(child=serializers.UUIDField(), write_only=True,
                                                       label='删除的课件id列表', help_text='删除的课件id列表', required=False,
                                                       allow_null=True)

    class Meta:
        model = LessonPeriod
        fields = ['name', 'desc', 'add_unit_id_list', 'delete_unit_id_list', 'add_lesson_file_id_list',
                  'add_lesson_file_id_list', 'delete_lesson_file_id_list', 'user_id', 'time']

    def update(self, instance, validated_data):
        user_id = validated_data.get('user_id')
        user = UserProfile.objects.get(id=user_id)
        if not user.is_teacher:
            raise serializers.ValidationError({'detail': '你不是老师，不能修改！'})
        teacher = user.teacher
        delete_lesson_file_id_list = validated_data.get('delete_lesson_file_id_list')
        if delete_lesson_file_id_list:
            for id in delete_lesson_file_id_list:
                file = File.objects.filter(id=id, if_delete=False)
                if file:
                    file = file[0]
                    try:
                        instance.lesson_file.remove(file)
                    except:
                        raise serializers.ValidationError({'detail': '课件未添加！不能删除'})
                else:
                    raise serializers.ValidationError({'detail': '文件不存在！操作终止'})
        add_lesson_file_id_list = validated_data.get('add_lesson_file_id_list')
        if add_lesson_file_id_list:
            for id in add_lesson_file_id_list:
                file = File.objects.filter(id=id)
                if file:
                    file = file[0]
                    try:
                        disk = file.disk
                        if disk.ower != user:
                            raise serializers.ValidationError({'detail': '这不是你的文件！不能添加'})
                        if disk.if_disable:
                            raise serializers.ValidationError({'detail': '你的网盘已被禁用！不能再使用'})
                        if disk.if_close:
                            raise serializers.ValidationError({'detail': '你的网盘已经关闭！先去开启再继续使用吧'})
                        if file.if_delete:
                            raise serializers.ValidationError({'detail': '该文件已被回收！不能选择'})
                        instance.lesson_file.add(file)
                    except:
                        raise serializers.ValidationError({'detail': '课件已存在！勿重复添加'})
                else:
                    raise serializers.ValidationError({'detail': '文件不存在！操作终止'})
        delete_unit_id_list = validated_data.get('delete_unit_id_list')
        if delete_unit_id_list:
            for id in delete_unit_id_list:
                try:
                    instance.unit.remove(Unit.objects.get(id=id))
                except:
                    raise serializers.ValidationError({'detail': '课件不存在！不能删除'})
        add_unit_id_list = validated_data.get('add_unit_id_list')
        if add_unit_id_list:
            for id in add_unit_id_list:
                unit = Unit.objects.filter(id=id)
                if unit:
                    unit = unit[0]
                    if (unit.semester.post_code == instance.schedule_lesson.semester) and (
                            unit.teacher == user.teacher) and (unit.lesson == instance.schedule_lesson.lesson):
                        try:
                            instance.unit.add(unit)
                        except:
                            raise serializers.ValidationError({'detail': '章节已添加！不要重复添加'})
                    else:
                        raise serializers.ValidationError({'detail': '你不能添加另一门课程的大纲！'})
                else:
                    raise serializers.ValidationError({'detail': '章节不存在！'})
        name = validated_data.get('name')
        if name:
            instance.name = name
        desc = validated_data.get('desc')
        if desc:
            instance.desc = desc
        time = validated_data.get('time')
        if time:
            instance.time = time
        try:
            instance.save()
        except:
            raise serializers.ValidationError({'detail': '课程大纲或课件重复！'})
        return instance


class HomeworkListSerializer(serializers.ModelSerializer):
    file = FileListSerializer()

    class Meta:
        model = Homework
        fields = '__all__'


class HomeworkCreateSerializer(serializers.ModelSerializer):
    user_id = serializers.HiddenField(default=serializers.CurrentUserDefault())
    # question_counter=serializers.IntegerField(min_value=0,default=1,required=False,allow_null=True,label='题目数',help_text='题目数')
    # total_score=serializers.IntegerField(min_value=0,default=100,required=False,allow_null=True,label='总分',help_text='总分')
    timeout = serializers.IntegerField(min_value=0, required=False, allow_null=True, label='完成时间限制（分钟）',
                                       help_text='完成时间限制（分钟）')

    class Meta:
        model = Homework
        fields = ['lesson_period', 'title', 'describe', 'timeout', 'limit_time', 'file', 'user_id']

    def create(self, validated_data):
        user_id = validated_data.get('user_id')
        user = UserProfile.objects.get(id=user_id)
        if not user.is_teacher:
            raise serializers.ValidationError({'detail': '你不是教师！不能布置作业'})
        lesson_period = validated_data.get('lesson_period')
        if lesson_period.schedule_lesson.teacher != user.teacher:
            raise serializers.ValidationError({"detail": '你不是该课时的老师！不能布置作业'})
        title = validated_data.get('title')
        describe = validated_data.get('describe')
        timeout = validated_data.get('timeout')
        limit_time = validated_data.get('limit_time')
        homework = Homework(user=user, lesson_period=lesson_period, title=title, describe=describe, timeout=timeout,
                            limit_time=limit_time)
        file = validated_data.get('file')
        if file:
            for f in file:
                disk = f.disk
                if disk.ower != user:
                    raise serializers.ValidationError({'detail': '这不是你的文件！不能添加'})
                if disk.if_disable:
                    raise serializers.ValidationError({'detail': '你的网盘已被禁用！不能再使用'})
                if disk.if_close:
                    raise serializers.ValidationError({'detail': '你的网盘已经关闭！先去开启再继续使用吧'})
                if f.if_delete:
                    raise serializers.ValidationError({'detail': '该文件已被回收！不能选择'})
                homework.file.add(f)
        homework.save()
        return homework


class HomeworkUpdateSerializer(serializers.ModelSerializer):
    user_id = serializers.HiddenField(default=serializers.CurrentUserDefault())
    add_file_id_list = serializers.ListField(child=serializers.UUIDField(), required=False, allow_null=True,
                                             write_only=True, label='添加文件id列表', help_text='添加文件id列表')
    delete_file_id_list = serializers.ListField(child=serializers.UUIDField(), required=False, allow_null=True,
                                                write_only=True, label='删除文件id列表', help_text='删除文件id列表')
    # question_counter=serializers.IntegerField(min_value=0,required=False,allow_null=True,label='题目数',help_text='题目数')
    timeout = serializers.IntegerField(min_value=0, required=False, allow_null=True, label='完成时间限制（分钟）',
                                       help_text='完成时间限制（分钟）')

    class Meta:
        model = Homework
        fields = ['title', 'describe', 'timeout', 'limit_time', 'add_file_id_list', 'delete_file_id_list', 'user_id']

    def update(self, instance, validated_data):
        user_id = validated_data.get('user_id')
        user = UserProfile.objects.get(id=user_id)
        if not user.is_teacher:
            raise serializers.ValidationError({'detail': '你不是教师！不能更改作业'})
        teacher = user.teacher
        if instance.lesson_period.schedule_lesson.teacher != teacher:
            raise serializers.ValidationError({'detail': '你不是该课程的老师！不能修改该作业'})
        title = validated_data.get('title')
        if title:
            instance.title = title
        describe = validated_data.get('describe')
        if describe:
            instance.describe = describe
        timeout = validated_data.get('timeout')
        if timeout:
            instance.timeout = timeout
        limit_time = validated_data.get('limit_time')
        if limit_time:
            instance.limit_time = limit_time
        delete_file_id_list = validated_data.get('delete_file_id_list')
        if delete_file_id_list:
            for id in delete_file_id_list:
                file = File.objects.filter(id=id)
                if file:
                    file = file[0]
                    try:
                        instance.file.remove(file)
                    except:
                        raise serializers.ValidationError({'detail': '你没有添加该文件！不能删除'})
                else:
                    raise serializers.ValidationError({'detail': '文件不存在！'})
        add_file_id_list = validated_data.get('add_file_id_list')
        if add_file_id_list:
            for id in add_file_id_list:
                file = File.objects.filter(id=id)
                if file:
                    file = file[0]
                    disk = file.disk
                    if disk.ower != user:
                        raise serializers.ValidationError({'detail': '这不是你的文件！不能添加'})
                    if disk.if_disable:
                        raise serializers.ValidationError({'detail': '你的网盘已被禁用！不能再使用'})
                    if disk.if_close:
                        raise serializers.ValidationError({'detail': '你的网盘已经关闭！先去开启再继续使用吧'})
                    if file.if_delete:
                        raise serializers.ValidationError({'detail': '该文件已被回收！不能选择'})
                    try:
                        instance.file.add(file)
                    except:
                        raise serializers.ValidationError({'detail': '该文件已添加！不要重复添加！'})
                else:
                    raise serializers.ValidationError({'detail': '该文件不存在！'})
        instance.save()
        return instance


class QuestionImageListSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionImage
        fields = '__all__'


class QuestionImageCreateSerializer(serializers.ModelSerializer):
    user_id = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = QuestionImage
        fields = '__all__'

    def create(self, validated_data):
        user_id = validated_data.get('user_id')
        user = UserProfile.objects.get(id=user_id)
        if not user.is_teacher:
            raise serializers.ValidationError({'detail': '你不是教师！不能编辑题目图片！'})
        teacher = user.teacher
        question = validated_data.get('question')
        schedule_lesson = question.homework.lesson_period.schedule_lesson
        if teacher != schedule_lesson.teacher:
            raise serializers.ValidationError({'detail': '你不是该课程的教师！不能编辑题目图片'})
        if question.image_count >= 9:
            raise serializers.ValidationError({'detail': '一题最多可添加9张图片！不能再添加'})
        try:
            question_image = QuestionImage.objects.create(number=validated_data.get('number'),
                                                          image=validated_data.get('image'), question=question)
            question.image_count += 1
            question.save()
            return question_image
        except:
            raise serializers.ValidationError({'detail': '图片编号冲突！请重新编辑'})


class QuestionImageUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionImage
        fields = ['number']


class QuestionListSerializer(serializers.ModelSerializer):
    image = QuestionImageListSerializer()
    knowladge_labels = KnowledgeLabelListSerializer()

    class Meta:
        model = Question
        # fields='__all__'
        exclude = ['analysis']


class QuestionCreateSerializer(serializers.ModelSerializer):
    user_id = serializers.HiddenField(default=serializers.CurrentUserDefault())
    id = serializers.IntegerField(read_only=True)
    number = serializers.IntegerField(required=True, min_value=1, label='编号', help_text='编号')
    score = serializers.IntegerField(required=True, min_value=0, label='分值', help_text='分值')
    class Meta:
        model = Question
        fields = ['user_id', 'id', 'homework', 'knowledge_labels', 'question_type', 'number', 'question', 'analysis',
                  'score', 'if_auto_correct', 'if_answer_update']
    def create(self, validated_data):
        user_id = validated_data.get('user_id')
        user = UserProfile.objects.get(id=user_id)
        if not user.is_teacher:
            raise serializers.ValidationError({'detail': '你不是教师！不能添加题目'})
        teacher = user.teacher
        homework = validated_data.get('homework')
        homework_lesson_period_schedule_lesson = homework.lesson_period.schedule_lesson
        if homework_lesson_period_schedule_lesson.teacher != teacher:
            raise serializers.ValidationError({'detail': '你不是该课程的老师！不能创建问题'})
        question_type = validated_data.get('question_type')
        que = validated_data.get('question')
        number = validated_data.get('number')
        analysis = validated_data.get('analysis')
        score = validated_data.get('score')
        if_auto_correct = validated_data.get('if_auto_correct')
        if_answer_update = validated_data.get('if_answer_update')
        if if_auto_correct and (question_type not in ['DanXuan', 'DuoXuan', 'PanDuan', 'TianKong']):
            raise serializers.ValidationError({'detail': '非选择题、判断题、填空题，不能自动批改！'})
        if (not if_auto_correct) and (question_type in ['DanXuan','DuoXuan','PanDuan']):
            raise serializers.ValidationError({'detail':'选择题可以自动批改！无需设置手动批改'})
        if if_auto_correct and if_answer_update:
            raise serializers.ValidationError({'detail': '该次作业已设置为自动批改，不能设置为学生可以更改答案！'})
        question = Question(homework=homework, question=que, question_type=question_type, number=number,
                            analysis=analysis, score=score, if_auto_correct=if_auto_correct,
                            if_answer_update=if_answer_update)
        knowladge_labels = validated_data.get('knowladge_labels')
        for k_l in knowladge_labels:
            if k_l.teacher != teacher:
                raise serializers.ValidationError({"detail": "你不是该标签的老师，不能添加该知识点标签！"})
            if k_l.lesson != homework_lesson_period_schedule_lesson.lesson:
                raise serializers.ValidationError({'detail': '该知识点标签不属于该课程！不能添加'})
            if k_l.semester != homework_lesson_period_schedule_lesson.semester:
                raise serializers.ValidationError({'detail': '该知识点标签不属于该学期！不能添加'})
            try:
                question.knowledge_labels.add(k_l)
                k_l.question_count += 1
                k_l.save()
            except:
                raise serializers.ValidationError({'detail': '知识点标签重复！'})
        question.save()
        if question.question_type=='TianKong':
            blank_count=que.count('(##)')
            if blank_count:
                blank_score=score/blank_count
                for i in range(blank_count):
                    TianKongBlank.objects.create(question=question,number=i,score=blank_score)
            else:
                question.delete()
                raise serializers.ValidationError({'detail':'该题目没有设置填空！'})
        homework.question_counter += 1
        homework.total_score += score
        homework.save()
        return question


class QuestionUpdateSerializer(serializers.ModelSerializer):
    knowledge_label_add_id_list = serializers.ListField(child=serializers.IntegerField(), required=False,
                                                        allow_null=True, write_only=True, help_text='新增的知识点标签id列表',
                                                        label='新增的知识点标签id列表')
    knowledge_label_remove_id_list = serializers.ListField(child=serializers.IntegerField(), required=False,
                                                           allow_null=True, write_only=True, help_text='删除的知识点标签id列表',
                                                           label='删除的知识点标签id列表')
    number = serializers.IntegerField(required=True, min_value=1, label='编号', help_text='编号')
    score = serializers.IntegerField(required=True, min_value=1, label='分值', help_text='分值')
    user_id = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Question
        fields = ['user_id', 'number', 'question', 'analysis', 'score', 'knowledge_label_add_id_list',
                  'knowledge_label_remove_id_list']

    def update(self, instance, validated_data):
        user_id = validated_data.get('user_id')
        user = UserProfile.objects.get(id=user_id)
        if not user.is_teacher:
            raise serializers.ValidationError({'detail': '你不是教师！不能更改该问题'})
        teacher = user.teacher
        schedule_lesson = instance.homework.lesson_period.schedule
        if schedule_lesson.teacher != teacher:
            raise serializers.ValidationError({'detail': '你不是该课程的老师！不能更改该作业'})
        number = validated_data.get('number')
        if number:
            q = Question.objects.filter(homework=instance.homework, number=number)
            if q:
                raise serializers.ValidationError({'detail': '该次作业该编号已存在！'})
            instance.number = number
        instance.question = validated_data.get('question', instance.question)
        instance.analysis = validated_data.get('analysis', instance.analysis)
        homework = instance.homework
        homework -= instance.score
        instance.score = validated_data.get('score', instance.score)
        knowledge_label_remove_id_list = validated_data.get('knowledge_label_remove_id_list')
        if knowledge_label_remove_id_list:
            for id in knowledge_label_remove_id_list:
                lab = KnowledgeLabel.objects.filter(id=id)
                if lab:
                    lab = lab[0]
                    try:
                        instance.knowledge_labels.remove(lab)
                        lab.question_count -= 1
                        lab.save()
                    except:
                        raise serializers.ValidationError({'detail': '未添加该标签！不能删除！'})
                else:
                    raise serializers.ValidationError({'detail': '知识点标签不存在！'})
        knowledge_label_add_id_list = validated_data.get('knowledge_label_add_id_list')
        if knowledge_label_add_id_list:
            for id in knowledge_label_add_id_list:
                k_l = KnowledgeLabel.objects.filter(id=id)
                if k_l:
                    k_l = k_l[0]
                    if k_l.teacher != instance.teacher:
                        raise serializers.ValidationError({"detail": "你不是该标签的老师，不能添加该知识点标签！"})
                    if k_l.lesson != instance.lesson:
                        raise serializers.ValidationError({'detail': '该知识点标签不属于该课程！不能添加'})
                    if k_l.semester != instance.semester:
                        raise serializers.ValidationError({'detail': '该知识点标签不属于该学期！不能添加'})
                    try:
                        instance.knowledge_labels.add(k_l)
                        k_l.unit_count += 1
                        k_l.save()
                    except:
                        raise serializers.ValidationError({'detail': '知识点标签重复！'})
                else:
                    raise serializers.ValidationError({'detail': '该知识点标签不存在！'})
        instance.save()
        homework += instance.score
        homework.save()
        return instance


class ChoiceListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = '__all__'


class ChoiceCreateSerializer(serializers.ModelSerializer):
    user_id = serializers.HiddenField(default=serializers.CurrentUserDefault())
    id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Choice
        fields = ['question', 'choice', 'content', 'user_id', 'id']

    def create(self, validated_data):
        user_id = validated_data.get('user_id')
        user = UserProfile.objects.get(id=user_id)
        if not user.is_teacher:
            raise serializers.ValidationError({'detail': '你不是教师！不能添加题目选项'})
        teacher = user.teacher
        question = validated_data.get('question')
        if question.homework.lesson_period.schedule_lesson.teacher != teacher:
            raise serializers.ValidationError({'detail': '你不是该课程的教师！不能你添加题目选项'})
        if question.question_type not in ['DanXuan', 'DuoXuan']:
            raise serializers.ValidationError({'detail': "该题不是选择题！不能添加选项"})
        q = Question.objects.filter(question=question, choice=validated_data.get('choice'))
        if q:
            raise serializers.ValidationError({'detail': '该题该选项已存在！'})
        choice = Choice.objects.create(question=question, choice=validated_data.get('choice'),
                                       content=validated_data.get('content'))
        return choice


class ChoiceUpdateSerializer(serializers.ModelSerializer):
    user_id = serializers.HiddenField(default=serializers.CurrentUserDefault())
    id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Choice
        fields = ['choice', 'content', 'user_id', 'id']

    def update(self, instance, validated_data):
        user_id = validated_data.get('user_id')
        user = UserProfile.objects.get(id=user_id)
        if not user.is_teacher:
            raise serializers.ValidationError({'detail': '你不是教师！不能添加题目选项'})
        teacher = user.teacher
        question = instance.question
        if question.homework.lesson_period.schedule_lesson.teacher != teacher:
            raise serializers.ValidationError({'detail': '你不是该课程的教师！不能你添加题目选项'})
        q = Question.objects.filter(question=question, choice=validated_data.get('choice'))
        if q:
            raise serializers.ValidationError({'detail': '该题该选项已存在！'})
        instance.choice = validated_data.get('choice', instance.choice)
        instance.content = validated_data.get('content', instance.content)
        instance.save()
        return instance


class HomeworkScoreCreateSerializer(serializers.ModelSerializer):
    user_id = serializers.HiddenField(default=serializers.CurrentUserDefault())
    id = serializers.IntegerField(read_only=True)

    class Meta:
        model = HomeworkScore
        fields = ['homework', 'user_id', 'id']

    def create(self, validated_data):
        user_id = validated_data.get('user_id')
        user = UserProfile.objects.get(id=user_id)
        if not user.is_student:
            raise serializers.ValidationError({'detail': '你不是学生！不能开始作业'})
        homework = validated_data.get('homework')
        schedule_lesson = homework.lesson_period.schedule_lesson
        student = user.student
        score = Score.objects.filter(schedule_lesson=schedule_lesson, student=student)
        if not score:
            raise serializers.ValidationError({'detail': '你不是该课程班级学生！不能开始作业'})
        if homework.limit_time < datetime.now():
            raise serializers.ValidationError({'detail': '该作业已过期！不能再开始作业'})
        h_s = HomeworkScore.objects.filter(student=student, homework=homework)
        if h_s:
            raise serializers.ValidationError({'detail': '你已经开始答题了！不能再重新开始'})
        homework_score = HomeworkScore.objects.create(student=student, homework=homework)
        return homework_score


class HomeworkScoreListSerializer(serializers.ModelSerializer):
    class Meta:
        model = HomeworkScore
        fields = '__all__'


class HomeworkScoreUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = HomeworkScore
        fields = ['if_submit']

    def update(self, instance, validated_data):
        if_submit = validated_data.get('if_submit')
        if not if_submit:
            raise serializers.ValidationError({'detail': '你不能更改作业为未提交！'})
        instance.if_submit = if_submit
        instance.save()
        return instance


class ChoiceTrueAnswerListSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChoiceTrueAnswer
        fields = '__all__'


class ChoiceTrueAnswerCreateSerializer(serializers.ModelSerializer):
    user_id = serializers.HiddenField(default=serializers.CurrentUserDefault())
    id = serializers.IntegerField(read_only=True)

    class Meta:
        model = ChoiceTrueAnswer
        fields = ['id', 'user_id', 'question', 'choice']

    def create(self, validated_data):
        user_id = validated_data.get('user_id')
        user = UserProfile.objects.get(id=user_id)
        if not user.is_teacher:
            raise serializers.ValidationError({'detail': '你不是教师！不能添加正确选项'})
        teacher = user.teacher
        question = validated_data.get('question')
        if teacher != question.homework.lesson_period.schedule_lesson.teacher:
            raise serializers.ValidationError({'detail': '你不是该班级的教师！不能添加正确选项'})
        question_type = question.question_type
        if question_type not in ['DanXuan', 'DuoXuan']:
            raise serializers.ValidationError({'detail': '该题不是选择题！不能添加正确选项！'})
        if question_type == 'DanXuan':
            choice_true_answer = ChoiceTrueAnswer.objects.filter(question=question)
            if choice_true_answer:
                raise serializers.ValidationError({'detail': '该题为单选题，已存在一个正确选项，不能再添加正确选项！'})
        choice = validated_data.get('choice')
        if choice.question != question:
            raise serializers.ValidationError({'detail': '你不能添加其他题的选项为正确答案！'})
        choice_true_answer = ChoiceTrueAnswer.objects.filter(question=question, choice=choice)
        if choice_true_answer:
            raise serializers.ValidationError({'detail': '你已添加这个选项为正确答案！不能重复添加'})
        choice_true_answer = ChoiceTrueAnswer.objects.create(question=question, choice=choice)
        return choice_true_answer


class ChoiceTrueAnswerUpdateSerializer(serializers.ModelSerializer):
    user_id = serializers.HiddenField(default=serializers.CurrentUserDefault())
    id = serializers.IntegerField(read_only=True)

    class Meta:
        model = ChoiceTrueAnswer
        fields = ['id', 'user_id', 'choice']

    def update(self, instance, validated_data):
        user_id = validated_data.get('user_id')
        user = UserProfile.objects.get(id=user_id)
        if not user.is_teacher:
            raise serializers.ValidationError({'detail': '你不是教师！不能添加正确选项'})
        teacher = user.teacher
        if teacher != instance.question.homework.lesson_period.schedule_lesson.teacher:
            raise serializers.ValidationError({'detail': '你不是该班级的教师！不能添加正确选项'})
        question = instance.question
        choice = validated_data.get('choice')
        if choice.question != question:
            raise serializers.ValidationError({'detail': '你不能添加其他题的选项为正确答案！'})
        if question.question_type == 'DuoXuan':
            choice_true_answer = ChoiceTrueAnswer.objects.filter(question=question, choice=choice)
            if choice_true_answer:
                raise serializers.ValidationError({'detail': '你已添加这个选项为正确答案！不能重复添加'})
        instance.choice = choice
        instance.save()
        return instance


class StudentChoiceAnswerListSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentChoiceAnswer
        fields = '__all__'


class StudnetChoiceAnswerCreateSerializer(serializers.ModelSerializer):
    user_id = serializers.HiddenField(default=serializers.CurrentUserDefault())
    id = serializers.IntegerField(read_only=True)
    class Meta:
        model = StudentChoiceAnswer
        fields = ['choice', 'user_id', 'question', 'id']
    def create(self, validated_data):
        user_id = validated_data.get('user_id')
        user = UserProfile.objects.get(id=user_id)
        if not user.is_student:
            raise serializers.ValidationError({'detail': '你不是学生！不能提交题目选项'})
        question = validated_data.get('question')
        schedule_lesson = question.homework.lesson_period.schedule_lesson
        student = user.student
        score = Score.objects.filter(schedule_lesson=schedule_lesson, student=student)
        if not score:
            raise serializers.ValidationError({'detail': '你不是该课程班级学生！不能提交题目选项'})
        homework = question.homework
        if homework.limit_time < datetime.now():
            raise serializers.ValidationError({'detail': '该作业已过期！不能再提交'})
        homework_score = HomeworkScore.objects.filter(homework=homework, student=student)
        if not homework_score:
            raise serializers.ValidationError({'detail': '你还没有开始作业！不能提交'})
        if homework.timeout:
            homework_score = homework_score[0]
            over_time = homework_score.create_time + timedelta(hours=0, minutes=homework.timeout, seconds=0)
            if datetime.now() > over_time:
                raise serializers.ValidationError({'detail': '该作业已超出限定时间！不能再继续提交'})
        question_type = question.question_type
        if question_type not in ['DanXuan', 'DuoXuan']:
            raise serializers.ValidationError({'detail': '该题不是选择题！你不能添加选项'})
        if question_type == 'DanXuan':
            student_choice_answer = StudentChoiceAnswer.objects.filter(question=question, student=student)
            if student_choice_answer:
                raise serializers.ValidationError({'detail': '该题为单选题！你已经添加了选项，不能再添加选项！'})
        choice = validated_data.get('choice')
        if choice.question != question:
            raise serializers.ValidationError({'detail': '你不能选择其他题目的选项！'})
        student_choice_answer = StudentChoiceAnswer.objects.filter(question=question, student=student, choice=choice)
        if student_choice_answer:
            raise serializers.ValidationError({'detail': '你已经添加了该选项，不能再重复添加！'})
        student_choice_answer = StudentChoiceAnswer.objects.create(choice=choice, question=question, student=student)
        return student_choice_answer


class StudentChoiceAnswerUpdateSerializer(serializers.ModelSerializer):
    user_id = serializers.HiddenField(default=serializers.CurrentUserDefault())
    id = serializers.IntegerField(read_only=True)

    class Meta:
        model = StudentChoiceAnswer
        fields = ['user_id', 'id', 'choice']

    def update(self, instance, validated_data):
        user_id = validated_data.get('user_id')
        user = UserProfile.objects.get(id=user_id)
        if not user.is_student:
            raise serializers.ValidationError({'detail': '你不是学生！不能提交题目选项'})
        student = user.student
        if instance.student != student:
            raise serializers.ValidationError({'detail': '你不能更改别人的选项答案'})
        choice = validated_data.get('choice')
        question = instance.question
        if choice.question != question:
            raise serializers.ValidationError({'detail': '你不能添加别的题目的选项！'})
        if question.question_type == 'DuoXuan':
            raise serializers.ValidationError({'detail': '多选题不能更改答案，只能删除和添加！'})
        homework = question.homework
        if homework.limit_time < datetime.now():
            raise serializers.ValidationError({'detail': '该作业已过期！不能再更改'})
        homework_score = HomeworkScore.objects.filter(homework=homework, student=student)
        homework_score = homework_score[0]
        if homework_score.if_submit:
            raise serializers.ValidationError({'detail': '你已经提交了答案，不能再更改选项！'})
        if homework.timeout:
            over_time = homework_score.create_time + timedelta(hours=0, minutes=homework.timeout, seconds=0)
            if datetime.now() > over_time:
                raise serializers.ValidationError({'detail': '该作业已超出限定时间！不能再更改'})
        instance.choice = choice
        instance.save()
        return instance


class PanDuanTrueAnswerListSerializer(serializers.ModelSerializer):
    class Meta:
        model = PanDuanTrueAnswer
        fields = '__all__'


class PanDuanTrueAnswerCreateSerializer(serializers.ModelSerializer):
    user_id = serializers.HiddenField(default=serializers.CurrentUserDefault())
    id = serializers.IntegerField(read_only=True)

    class Meta:
        model = PanDuanTrueAnswer
        fields = ['question', 'answer', 'user_id', 'id']

    def create(self, validated_data):
        user_id = validated_data.get('user_id')
        user = UserProfile.objects.get(id=user_id)
        if not user.is_teacher:
            raise serializers.ValidationError({'detail': '你不是教师！不能添加创建答案'})
        teacher = user.teacher
        question = validated_data.get('question')
        if teacher != question.homework.lesson_period.schedule_lesson.teacher:
            raise serializers.ValidationError({'detail': '你不是该班级的教师！不能添加正确选项'})
        question_type = question.question_type
        if question_type != 'PanDuan':
            raise serializers.ValidationError({'detail': '该题不是选择题！不能添加正确选项！'})
        a = PanDuanTrueAnswer.objects.filter(question=question)
        if a:
            raise serializers.ValidationError({'detail': '你已经创建了该题的正确答案！不能再创建了'})
        panduan_true_answer = PanDuanTrueAnswer.objects.create(question=question, answer=validated_data.get('answer'))
        return panduan_true_answer


class PanDuanTrueAnswerUpdateSerializer(serializers.ModelSerializer):
    user_id = serializers.HiddenField(default=serializers.CurrentUserDefault())
    id = serializers.IntegerField(read_only=True)

    class Meta:
        model = PanDuanTrueAnswer
        fields = ['answer', 'user_id', 'id']

    def update(self, instance, validated_data):
        user_id = validated_data.get('user_id')
        user = UserProfile.objects.get(id=user_id)
        if not user.is_teacher:
            raise serializers.ValidationError({'detail': '你不是教师！不能添加创建答案'})
        teacher = user.teacher
        question = instance.question
        if teacher != question.homework.lesson_period.schedule_lesson.teacher:
            raise serializers.ValidationError({'detail': '你不是该班级的教师！不能更改正确选项'})
        instance.answer = validated_data.get('answer', instance.answer)
        instance.save()
        return instance


class StudentPanDuanAnswerListSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentPanDuanAnswer
        fields = '__all__'


class StudentPanDuanAnswerCreateSerializer(serializers.ModelSerializer):
    user_id = serializers.HiddenField(default=serializers.CurrentUserDefault())
    id = serializers.IntegerField(read_only=True)
    class Meta:
        model = StudentPanDuanAnswer
        fields = ['user_id','id','question','answer']
    def create(self, validated_data):
        user_id = validated_data.get('user_id')
        user = UserProfile.objects.get(id=user_id)
        if not user.is_student:
            raise serializers.ValidationError({'detail': '你不是学生！不能提交题目选项'})
        question = validated_data.get('question')
        schedule_lesson = question.homework.lesson_period.schedule_lesson
        student = user.student
        score = Score.objects.filter(schedule_lesson=schedule_lesson, student=student)
        if not score:
            raise serializers.ValidationError({'detail': '你不是该课程班级学生！不能提交题目选项'})
        homework = question.homework
        if homework.limit_time < datetime.now():
            raise serializers.ValidationError({'detail': '该作业已过期！不能再提交'})
        homework_score = HomeworkScore.objects.filter(homework=homework, student=student)
        if not homework_score:
            raise serializers.ValidationError({'detail': '你还没有开始作业！不能提交'})
        if homework.timeout:
            homework_score = homework_score[0]
            over_time = homework_score.create_time + timedelta(hours=0, minutes=homework.timeout, seconds=0)
            if datetime.now() > over_time:
                raise serializers.ValidationError({'detail': '该作业已超出限定时间！不能再继续作业'})
        question_type = question.question_type
        if question_type!='PanDuan':
            raise serializers.ValidationError({'detail': '该题不是判断题！你不能添加判断答案'})
        student_panduan_answer = StudentChoiceAnswer.objects.filter(question=question, student=student)
        if student_panduan_answer:
            raise serializers.ValidationError({'detail': '该题为判断题！你已经添加了答案，不能再添加！'})
        answer = validated_data.get('answer')
        student_panduan_answer = StudentPanDuanAnswer.objects.create(answer=answer, question=question, student=student)
        return student_panduan_answer

class StudentPanDuanAnswerUpdateSerializer(serializers.ModelSerializer):
    user_id = serializers.HiddenField(default=serializers.CurrentUserDefault())
    id = serializers.IntegerField(read_only=True)
    class Meta:
        model=StudentPanDuanAnswer
        fields=['answer','user_id','id']
    def update(self, instance, validated_data):
        user_id = validated_data.get('user_id')
        user = UserProfile.objects.get(id=user_id)
        if not user.is_student:
            raise serializers.ValidationError({'detail': '你不是学生！不能提交题目选项'})
        student = user.student
        if instance.student != student:
            raise serializers.ValidationError({'detail': '你不能更改别人的选项答案'})
        answer = validated_data.get('answer')
        question = instance.question
        homework = question.homework
        if homework.limit_time < datetime.now():
            raise serializers.ValidationError({'detail': '该作业已过期！不能再更改'})
        homework_score = HomeworkScore.objects.filter(homework=homework, student=student)
        homework_score = homework_score[0]
        if homework_score.if_submit:
            raise serializers.ValidationError({'detail': '你已经提交了答案，不能再更改判断选项！'})
        if homework.timeout:
            over_time = homework_score.create_time + timedelta(hours=0, minutes=homework.timeout, seconds=0)
            if datetime.now() > over_time:
                raise serializers.ValidationError({'detail': '该作业已超出限定时间！不能再更改'})
        instance.answer = answer
        instance.save()
        return instance

class TianKongBlankListSerializer(serializers.ModelSerializer):
    class Meta:
        model=TianKongBlank
        fields='__all__'

class TianKongBlankUpdateSerializer(serializers.ModelSerializer):
    user_id = serializers.HiddenField(default=serializers.CurrentUserDefault())
    id = serializers.IntegerField(read_only=True)
    score=serializers.FloatField(min_value=0.0,label='分数',help_text='分数')
    class Meta:
        model=TianKongBlank
        fields=['user_id','id','score']
    def update(self, instance, validated_data):
        user_id=validated_data.get('user_id')
        user=UserProfile.objects.get(id=user_id)
        if not user.is_teacher:
            raise serializers.ValidationError({'detail':'你不是教师！不能更改填空题目'})
        teacher = user.teacher
        if teacher != instance.question.homework.lesson_period.schedule_lesson.teacher:
            raise serializers.ValidationError({'detail': '你不是该班级的教师！不能添加正确选项'})
        question = instance.question
        question.score -=instance.score
        instance.score=validated_data.get('score',instance.score)
        instance.save()
        question.score += instance.score
        question.save()
        return instance

class TianKongTrueAnswerListSerializer(serializers.ModelSerializer):
    class Meta:
        model=TianKongTrueAnswer
        fields='__all__'

class TianKongTrueAnswerCreateSerializer(serializers.ModelSerializer):
    user_id = serializers.HiddenField(default=serializers.CurrentUserDefault())
    id = serializers.IntegerField(read_only=True)
    class Meta:
        model=TianKongTrueAnswer
        fields=['user_id','id','blank','answer']

    def create(self, validated_data):
        user_id = validated_data.get('user_id')
        user = UserProfile.objects.get(id=user_id)
        if not user.is_teacher:
            raise serializers.ValidationError({'detail': '你不是教师！不能添加创建答案'})
        teacher = user.teacher
        blank = validated_data.get('blank')
        if teacher != blank.question.homework.lesson_period.schedule_lesson.teacher:
            raise serializers.ValidationError({'detail': '你不是该班级的教师！不能添加填空答案！'})
        tiankong_true_answer=TianKongTrueAnswer.objects.filter(blank=blank)
        if tiankong_true_answer:
            raise serializers.ValidationError({'detail':'该空已设置正确选项！不能再设置！你可以设置其他答案'})
        tiankong_true_answer = TianKongTrueAnswer.objects.create(blank=blank,answer=validated_data.get('answer'))
        return tiankong_true_answer

class TianKongTrueAnswerUpdateSerializer(serializers.ModelSerializer):
    user_id = serializers.HiddenField(default=serializers.CurrentUserDefault())
    id = serializers.IntegerField(read_only=True)
    class Meta:
        model=TianKongTrueAnswer
        fields=['user_id','id','answer']
    def update(self, instance, validated_data):
        user_id = validated_data.get('user_id')
        user = UserProfile.objects.get(id=user_id)
        if not user.is_teacher:
            raise serializers.ValidationError({'detail': '你不是教师！不能添加创建答案'})
        teacher = user.teacher
        blank = instance.blank
        if teacher != blank.question.homework.lesson_period.schedule_lesson.teacher:
            raise serializers.ValidationError({'detail': '你不是该班级的教师！不能添加填空答案！'})
        instance.answer=validated_data.get('answer',instance.answer)
        instance.save()
        return instance

class TianKongOtherAnswerListSerializer(serializers.ModelSerializer):
    class Meta:
        model=TianKongOtherAnswer
        fields='__all__'

class TianKongOtherAnswerCreateSerializer(serializers.ModelSerializer):
    user_id = serializers.HiddenField(default=serializers.CurrentUserDefault())
    id = serializers.IntegerField(read_only=True)
    class Meta:
        model = TianKongOtherAnswer
        fields = ['user_id', 'id', 'blank', 'other_answer']
    def create(self, validated_data):
        user_id = validated_data.get('user_id')
        user = UserProfile.objects.get(id=user_id)
        if not user.is_teacher:
            raise serializers.ValidationError({'detail': '你不是教师！不能添加创建答案'})
        teacher = user.teacher
        blank = validated_data.get('blank')
        if teacher != blank.question.homework.lesson_period.schedule_lesson.teacher:
            raise serializers.ValidationError({'detail': '你不是该班级的教师！不能添加填空其他答案！'})
        other_answer=validated_data.get('other_answer')
        tiankong_other_answer = TianKongOtherAnswer.objects.filter(blank=blank,other_answer=other_answer)
        if tiankong_other_answer:
            raise serializers.ValidationError({'detail':'你已经添加了这个答案！不要重复添加'})
        tiankong_other_answer = TianKongOtherAnswer.objects.create(blank=blank, other_answer=other_answer)
        if not blank.if_other_answer:
            blank.if_other_answer=True
            blank.save()
        return tiankong_other_answer

class TianKongOtherAnswerUpdateSerializer(serializers.ModelSerializer):
    user_id = serializers.HiddenField(default=serializers.CurrentUserDefault())
    id = serializers.IntegerField(read_only=True)
    class Meta:
        model=TianKongOtherAnswer
        fields=['user_id','id','other_answer']
    def update(self, instance, validated_data):
        user_id = validated_data.get('user_id')
        user = UserProfile.objects.get(id=user_id)
        if not user.is_teacher:
            raise serializers.ValidationError({'detail': '你不是教师！不能添加创建答案'})
        teacher = user.teacher
        blank = instance.blank
        if teacher != blank.question.homework.lesson_period.schedule_lesson.teacher:
            raise serializers.ValidationError({'detail': '你不是该班级的教师！不能更改填空其他答案！'})
        other_answer=validated_data.get('other_answer')
        oth=TianKongOtherAnswer.objects.filter(blank=blank,other_answer=other_answer)
        if oth:
            raise serializers.ValidationError({'detail':'你已经添加了这个答案！不要重复添加'})
        instance.other_answer=other_answer
        instance.save()
        return instance

class StudentTianKongAnswerListSerializer(serializers.ModelSerializer):
    class Meta:
        model=StudentTianKongAnswer
        fields='__all__'

class StudentTianKongAnswerCreateSerializer(serializers.ModelSerializer):
    user_id = serializers.HiddenField(default=serializers.CurrentUserDefault())
    id = serializers.IntegerField(read_only=True)
    class Meta:
        model=StudentTianKongAnswer
        fields=['id','user_id','blank','answer']
    def create(self, validated_data):
        user_id = validated_data.get('user_id')
        user = UserProfile.objects.get(id=user_id)
        if not user.is_student:
            raise serializers.ValidationError({'detail': '你不是学生！不能提交题目选项'})
        blank = validated_data.get('blank')
        question=blank.question
        schedule_lesson = question.homework.lesson_period.schedule_lesson
        student = user.student
        score = Score.objects.filter(schedule_lesson=schedule_lesson, student=student)
        if not score:
            raise serializers.ValidationError({'detail': '你不是该课程班级学生！不能提交题目选项'})
        homework = question.homework
        if homework.limit_time < datetime.now():
            raise serializers.ValidationError({'detail': '该作业已过期！不能再提交'})
        homework_score = HomeworkScore.objects.filter(homework=homework, student=student)
        if not homework_score:
            raise serializers.ValidationError({'detail': '你还没有开始作业！不能提交'})
        if homework.timeout:
            homework_score = homework_score[0]
            over_time = homework_score.create_time + timedelta(hours=0, minutes=homework.timeout, seconds=0)
            if datetime.now() > over_time:
                raise serializers.ValidationError({'detail': '该作业已超出限定时间！不能再继续作业'})
        student_tiankong_answer = StudentTianKongAnswer.objects.filter(blank=blank,student=student)
        if student_tiankong_answer:
            raise serializers.ValidationError({'detail': '你已经填该空，不能再填！'})
        answer = validated_data.get('answer')
        student_panduan_answer = StudentTianKongAnswer.objects.create(answer=answer, blank=blank, student=student)
        return student_panduan_answer

class StudentTianKongAnswerUpdateSerializer(serializers.ModelSerializer):
    user_id=serializers.HiddenField(default=serializers.CurrentUserDefault())
    id=serializers.IntegerField(read_only=True)
    class Meta:
        model=StudentTianKongAnswer
        fields=['answer','id','user_id']
    def update(self, instance, validated_data):
        user_id = validated_data.get('user_id')
        user = UserProfile.objects.get(id=user_id)
        if not user.is_student:
            raise serializers.ValidationError({'detail': '你不是学生！不能提交题目选项'})
        student = user.student
        if instance.student != student:
            raise serializers.ValidationError({'detail': '你不能更改别人的选项答案'})
        answer = validated_data.get('answer')
        blank=instance.blank
        question = blank.question
        homework = question.homework
        if homework.limit_time < datetime.now():
            raise serializers.ValidationError({'detail': '该作业已过期！不能再更改'})
        homework_score = HomeworkScore.objects.filter(homework=homework, student=student)
        homework_score = homework_score[0]
        if question.if_auto_correct:
            if homework_score.if_submit:
                raise serializers.ValidationError({'detail': '你已经提交了答案，不能再更改填空答案！'})
        if homework.timeout:
            over_time = homework_score.create_time + timedelta(hours=0, minutes=homework.timeout, seconds=0)
            if datetime.now() > over_time:
                raise serializers.ValidationError({'detail': '该作业已超出限定时间！不能再更改'})
        instance.answer = answer
        instance.save()
        return instance

class JianDaAnswerListSerializer(serializers.ModelSerializer):
    class Meta:
        model=JianDaAnswer
        fields='__all__'

class JianDaAnswerCreateSerializer(serializers.ModelSerializer):
    user_id = serializers.HiddenField(default=serializers.CurrentUserDefault())
    id = serializers.IntegerField(read_only=True)
    class Meta:
        model=JianDaAnswer
        fields=['user_id','id','question','answer']
    def create(self, validated_data):
        user_id = validated_data.get('user_id')
        user = UserProfile.objects.get(id=user_id)
        if not user.is_teacher:
            raise serializers.ValidationError({'detail': '你不是教师！不能添加创建答案'})
        teacher = user.teacher
        question = validated_data.get('question')
        if teacher != question.homework.lesson_period.schedule_lesson.teacher:
            raise serializers.ValidationError({'detail': '你不是该班级的教师！不能添加正确选项'})
        question_type = question.question_type
        if question_type != 'JianDa':
            raise serializers.ValidationError({'detail': '该题不是简答题！不能添加简答参考答案！'})
        a = JianDaAnswer.objects.filter(question=question)
        if a:
            raise serializers.ValidationError({'detail': '你已经创建了该题的参考答案！不能再创建了'})
        jianda_answer = JianDaAnswer.objects.create(question=question, answer=validated_data.get('answer'))
        return jianda_answer

class JianDaAnswerUpdateSerializer(serializers.ModelSerializer):
    user_id = serializers.HiddenField(default=serializers.CurrentUserDefault())
    id = serializers.IntegerField(read_only=True)
    class Meta:
        model=JianDaAnswer
        fields=['user_id','id','answer']
    def update(self, instance, validated_data):
        user_id = validated_data.get('user_id')
        user = UserProfile.objects.get(id=user_id)
        if not user.is_teacher:
            raise serializers.ValidationError({'detail': '你不是教师！不能更改答案'})
        teacher = user.teacher
        question = instance.question
        if teacher != question.homework.lesson_period.schedule_lesson.teacher:
            raise serializers.ValidationError({'detail': '你不是该班级的教师！不能更改参考答案'})
        instance.answer = validated_data.get('answer', instance.answer)
        instance.save()
        return instance

class StudentJianDaAnswerListSerializer(serializers.ModelSerializer):
    class Meta:
        model=StudentJianDaAnswer
        fields='__all__'

class StudentJianDaAnswerCreateSerializer(serializers.ModelSerializer):
    user_id = serializers.HiddenField(default=serializers.CurrentUserDefault())
    id = serializers.IntegerField(read_only=True)
    class Meta:
        model=StudentJianDaAnswer
        fields=['id','user_id','question','answer','if_auto_submit']
    def create(self, validated_data):
        user_id = validated_data.get('user_id')
        user = UserProfile.objects.get(id=user_id)
        if not user.is_student:
            raise serializers.ValidationError({'detail': '你不是学生！不能提交题目选项'})
        question = validated_data.get('question')
        schedule_lesson = question.homework.lesson_period.schedule_lesson
        student = user.student
        score = Score.objects.filter(schedule_lesson=schedule_lesson, student=student)
        if not score:
            raise serializers.ValidationError({'detail': '你不是该课程班级学生！不能提交简答题答案'})
        homework = question.homework
        if homework.limit_time < datetime.now():
            raise serializers.ValidationError({'detail': '该作业已过期！不能再提交'})
        homework_score = HomeworkScore.objects.filter(homework=homework, student=student)
        if not homework_score:
            raise serializers.ValidationError({'detail': '你还没有开始作业！不能提交'})
        if homework.timeout:
            homework_score = homework_score[0]
            over_time = homework_score.create_time + timedelta(hours=0, minutes=homework.timeout, seconds=0)
            if datetime.now() > over_time:
                raise serializers.ValidationError({'detail': '该作业已超出限定时间！不能再继续作业'})
        if_auto_submit=validated_data.get('if_auto_submit')
        if if_auto_submit:
            student_jianda_answer = StudentJianDaAnswer.objects.filter(question=question,if_auto_submit=False,student=student)
            if student_jianda_answer:
                raise serializers.ValidationError({'detail': '你已经提交简答答案，不能重复提交！'})
        answer = validated_data.get('answer')
        student_panduan_answer = StudentJianDaAnswer.objects.create(answer=answer, question=question,if_auto_submit=if_auto_submit, student=student)
        return student_panduan_answer

class StudentJianDaAnswerUpdateSerializer(serializers.ModelSerializer):
    user_id = serializers.HiddenField(default=serializers.CurrentUserDefault())
    id = serializers.IntegerField(read_only=True)
    class Meta:
        model=StudentJianDaAnswer
        fields=['id','user_id','answer']
    def update(self, instance, validated_data):
        user_id = validated_data.get('user_id')
        user = UserProfile.objects.get(id=user_id)
        if not user.is_student:
            raise serializers.ValidationError({'detail': '你不是学生！不能提交题目选项'})
        student = user.student
        if instance.student != student:
            raise serializers.ValidationError({'detail': '你不能更改别人的选项答案'})
        answer = validated_data.get('answer')
        question = instance.question
        homework = question.homework
        if homework.limit_time < datetime.now():
            raise serializers.ValidationError({'detail': '该作业已过期！不能再更改'})
        homework_score = HomeworkScore.objects.filter(homework=homework, student=student)
        homework_score = homework_score[0]
        if homework_score.if_submit:
            if not question.if_answer_update:
                raise serializers.ValidationError({'detail': '你已经提交了答案，不能再更改简答答案！'})
        if homework.timeout:
            over_time = homework_score.create_time + timedelta(hours=0, minutes=homework.timeout, seconds=0)
            if datetime.now() > over_time:
                raise serializers.ValidationError({'detail': '该作业已超出限定时间！不能再更改'})
        if instance.if_auto_submit:
            raise serializers.ValidationError({'detail':'你没有提交该简答题答案！不能更改'})
        instance.answer = answer
        instance.save()
        return instance

class OtherAnswerImageListSerializer(serializers.ModelSerializer):
    class Meta:
        model=OtherAnswerImage
        fields='__all__'

class OtherAnswerImageCreateSerializer(serializers.ModelSerializer):
    user_id = serializers.HiddenField(default=serializers.CurrentUserDefault())
    id = serializers.IntegerField(read_only=True)
    class Meta:
        model=OtherAnswerImage
        fields=['user_id','id','number','other_answer','image']
    def create(self, validated_data):
        user_id = validated_data.get('user_id')
        user = UserProfile.objects.get(id=user_id)
        if not user.is_teacher:
            raise serializers.ValidationError({'detail': '你不是教师！不能添加创建答案'})
        teacher = user.teacher
        other_answer = validated_data.get('other_answer')
        question = other_answer.question
        if teacher != question.homework.lesson_period.schedule_lesson.teacher:
            raise serializers.ValidationError({'detail':'你不是该课程的教师！不能添加答案图片'})
        if other_answer.image_count>=9:
            raise serializers.ValidationError({'detail':'最多可添加九张图片！'})
        number=validated_data.get('number')
        other_answer_image=OtherAnswerImage.objects.filter(number=number,other_answer=other_answer)
        if other_answer_image:
            raise serializers.ValidationError({'detail':'已存在该序号图片！请重新选择序号'})
        other_answer_image=OtherAnswerImage.objects.create(number=number,other_answer=other_answer,image=validated_data.get('image'))
        other_answer.image_count+=1
        other_answer.save()
        return other_answer_image

class OtherAnswerImageUpdateSerializer(serializers.ModelSerializer):
    user_id = serializers.HiddenField(default=serializers.CurrentUserDefault())
    id = serializers.IntegerField(read_only=True)
    class Meta:
        model=OtherAnswerImage
        fields=['user_id','id','number']
    def update(self, instance, validated_data):
        user_id = validated_data.get('user_id')
        user = UserProfile.objects.get(id=user_id)
        if not user.is_teacher:
            raise serializers.ValidationError({'detail': '你不是教师！不能更改答案'})
        teacher = user.teacher
        other_answer = instance.other_answer
        question = other_answer.question
        if teacher != question.homework.lesson_period.schedule_lesson.teacher:
            raise serializers.ValidationError({'detail': '你不是该班级的教师！不能更改参考答案'})
        number=validated_data.get('number')
        other_answer_image = OtherAnswerImage.objects.filter(number=number, other_answer=other_answer)
        if other_answer_image:
            raise serializers.ValidationError({'detail': '已存在该序号图片！请重新选择序号'})
        instance.number=number
        instance.save()
        return instance

class OtherAnswerListSerializer(serializers.ModelSerializer):
    other_answer_image=OtherAnswerImageListSerializer()
    file=FileListSerializer()
    class Meta:
        model=OtherAnswer
        fields='__all__'


class OtherAnswerCreateSerializer(serializers.ModelSerializer):
    user_id = serializers.HiddenField(default=serializers.CurrentUserDefault())
    id = serializers.IntegerField(read_only=True)
    class Meta:
        model=OtherAnswer
        fields=['text_answer','question','file','user_id','id']
    def create(self, validated_data):
        user_id = validated_data.get('user_id')
        user = UserProfile.objects.get(id=user_id)
        if not user.is_teacher:
            raise serializers.ValidationError({'detail': '你不是教师！不能添加创建答案'})
        teacher = user.teacher
        question = validated_data.get('question')

        if teacher != question.homework.lesson_period.schedule_lesson.teacher:
            raise serializers.ValidationError({'detail': '你不是该课程的教师！不能添加答案图片'})
        if question.question_type!='QiTa':
            raise serializers.ValidationError({'detail':'该题不是其他类型的题目！不能添加其他答案类型的答案！'})
        other_answer=OtherAnswer.objects.filter(question=question)
        if other_answer:
            raise serializers.ValidationError({'detail':'该题已创建了答案！不能再创建'})
        other_answer=OtherAnswer.objects.create(question=question,text_answer=validated_data.get('text_answer'))
        files=validated_data.get('file')
        if files:
            if len(files)>len(set(files)):
                raise serializers.ValidationError({'detail':'不能存在重复文件！'})
            for f in files:
                disk=f.disk
                if disk.ower_id!=user_id:
                    raise serializers.ValidationError({'detail':'你不能选择别人的网盘文件！'})
                if disk.if_close:
                    raise serializers.ValidationError({'detail':'你已经关闭了网盘，不能再继续使用网盘文件！'})
                if disk.if_disable:
                    raise serializers.ValidationError({'detail':'你的网盘已被禁用！不能再继续使用网盘文件'})
                if f.if_delete:
                    raise serializers.ValidationError({'detail':'该文件已被回收！不能再添加'})
                other_answer.file.add(f)
        other_answer.save()
        return other_answer

class OtherAnswerUpdateSerializer(serializers.ModelSerializer):
    user_id = serializers.HiddenField(default=serializers.CurrentUserDefault())
    id = serializers.IntegerField(read_only=True)
    add_file_id_list=serializers.ListField(child=serializers.UUIDField(),required=False,allow_empty=True,allow_null=True,label='添加的文件的id列表',help_text='添加的文件的id列表',write_only=True)
    remove_file_id_list=serializers.ListField(child=serializers.UUIDField(),required=False,allow_empty=True,allow_null=True,label='删除的文件的id列表',help_text='删除的文件的id列表',write_only=True)
    class Meta:
        model = OtherAnswer
        fields = ['text_answer', 'user_id', 'id','add_file_id_list','remove_file_id_list']
    def update(self, instance, validated_data):
        user_id = validated_data.get('user_id')
        user = UserProfile.objects.get(id=user_id)
        if not user.is_teacher:
            raise serializers.ValidationError({'detail': '你不是教师！不能更改答案'})
        teacher = user.teacher
        question = instance.question
        if teacher != question.homework.lesson_period.schedule_lesson.teacher:
            raise serializers.ValidationError({'detail': '你不是该班级的教师！不能更改答案'})
        text_answer=validated_data.get('text_answer')
        if text_answer:
            instance.text_answer=text_answer
        remove_file_id_list=validated_data.get('remove_file_id_list')
        if remove_file_id_list:
            if len(remove_file_id_list)>len(set(remove_file_id_list)):
                raise serializers.ValidationError({'detail':'删除的文件重复！'})
            for id in remove_file_id_list:
                file=File.objects.filter(id=id)
                if file:
                    file=file[0]
                    try:
                        instance.file.remove(file)
                    except:
                        raise serializers.ValidationError({'detail':'该文件未添加！不能删除'})
                else:
                    raise serializers.ValidationError({'detail':'删除的文件不存在！'})
        add_file_id_list=validated_data.get('add_file_id_list')
        if add_file_id_list:
            if len(add_file_id_list)>len(set(add_file_id_list)):
                raise serializers.ValidationError({'detail':'添加的文件重复！'})
            for id in add_file_id_list:
                file=File.objects.filter(id=id)
                if file:
                    file=file[0]
                    disk = file.disk
                    if disk.ower_id != user_id:
                        raise serializers.ValidationError({'detail': '你不能选择别人的网盘文件！'})
                    if disk.if_close:
                        raise serializers.ValidationError({'detail': '你已经关闭了网盘，不能再继续使用网盘文件！'})
                    if disk.if_disable:
                        raise serializers.ValidationError({'detail': '你的网盘已被禁用！不能再继续使用网盘文件'})
                    if file.if_delete:
                        raise serializers.ValidationError({'detail': '该文件已被回收！不能再添加'})
                    try:
                        instance.file.add(file)
                    except:
                        raise serializers.ValidationError({'detail':'文件已存在！不能再添加'})
                else:
                    raise serializers.ValidationError({'detail':'添加的文件不存在！'})
        try:
            instance.save()
            return instance
        except:
            raise serializers.ValidationError({'detail':'文件输入有误！'})


class StudentOtherAnswerImageListSerializer(serializers.ModelSerializer):
    class Meta:
        model=StudentOtherAnswerImage
        fields='__all__'


class StudentOtherAnswerImageCreateSerializer(serializers.ModelSerializer):
    user_id = serializers.HiddenField(default=serializers.CurrentUserDefault())
    id = serializers.IntegerField(read_only=True)
    class Meta:
        model=StudentOtherAnswerImage
        fields=['user_id','id','number','student_other_answer','image']
    def create(self, validated_data):
        user_id = validated_data.get('user_id')
        user = UserProfile.objects.get(id=user_id)
        if not user.is_student:
            raise serializers.ValidationError({'detail': '你不是学生！不能提交题目选项'})
        student = user.student
        student_other_answer = validated_data.get('student_other_answer')
        if student_other_answer.student!=student:
            raise serializers.ValidationError({'detail':'你不能添加图片到别人的答案！'})
        if student_other_answer.image_count>=9:
            raise serializers.ValidationError({'detail':'最多只能添加9张图片！'})
        question=student_other_answer.question
        homework = question.homework
        if homework.limit_time < datetime.now():
            raise serializers.ValidationError({'detail': '该作业已过期！不能再提交'})
        homework_score = HomeworkScore.objects.filter(homework=homework, student=student)
        if not homework_score:
            raise serializers.ValidationError({'detail': '你还没有开始作业！不能提交'})
        if homework.timeout:
            homework_score = homework_score[0]
            over_time = homework_score.create_time + timedelta(hours=0, minutes=homework.timeout, seconds=0)
            if datetime.now() > over_time:
                raise serializers.ValidationError({'detail': '该作业已超出限定时间！不能再继续作业'})
        number=validated_data.get('number')
        student_other_answer_image=StudentOtherAnswerImage.objects.filter(student_other_answer=student_other_answer,number=number)
        if student_other_answer_image:
            raise serializers.ValidationError({'detail':'已存在该序号图片！'})
        student_other_answer_image = StudentOtherAnswerImage.objects.create(student_other_answer=student_other_answer,number=number,image=validated_data.get('image'))
        student_other_answer.image_count+=1
        student_other_answer.save()
        return student_other_answer_image

class StudentOtherAnswerImageUpdateSerializer(serializers.ModelSerializer):
    user_id = serializers.HiddenField(default=serializers.CurrentUserDefault())
    id = serializers.IntegerField(read_only=True)
    class Meta:
        model=StudentOtherAnswerImage
        fields=['user_id','id','number']
    def update(self, instance, validated_data):
        user_id = validated_data.get('user_id')
        user = UserProfile.objects.get(id=user_id)
        if not user.is_student:
            raise serializers.ValidationError({'detail': '你不是学生！不能提交题目选项'})
        student = user.student
        student_other_answer = instance.student_other_answer
        if student_other_answer.student != student:
            raise serializers.ValidationError({'detail': '你不能添加图片到别人的答案！'})
        question = student_other_answer.question
        homework = question.homework
        if homework.limit_time < datetime.now():
            raise serializers.ValidationError({'detail': '该作业已过期！不能再提交'})
        homework_score = HomeworkScore.objects.filter(homework=homework, student=student)
        if not homework_score:
            raise serializers.ValidationError({'detail': '你还没有开始作业！不能提交'})
        if homework.timeout:
            homework_score = homework_score[0]
            over_time = homework_score.create_time + timedelta(hours=0, minutes=homework.timeout, seconds=0)
            if datetime.now() > over_time:
                raise serializers.ValidationError({'detail': '该作业已超出限定时间！不能再继续作业'})
        number=validated_data.get('number')
        if number:
            student_other_answer_image = StudentOtherAnswerImage.objects.filter(
                student_other_answer=student_other_answer, number=number)
            if student_other_answer_image:
                raise serializers.ValidationError({'detail':'已存在该序号图片！'})
            instance.number=number
        instance.save()
        return instance

class StudentOtherAnswerListSerializer(serializers.ModelSerializer):
    student_other_answer_image=StudentOtherAnswerImageListSerializer()
    class Meta:
        model=StudentOtherAnswer
        fields='__all__'

class StudentOtherAnswerCreateSerializer(serializers.ModelSerializer):
    user_id = serializers.HiddenField(default=serializers.CurrentUserDefault())
    id = serializers.IntegerField(read_only=True)
    class Meta:
        model=StudentOtherAnswer
        fields=['user_id','id','text_answer','question','file']
    def create(self, validated_data):
        user_id = validated_data.get('user_id')
        user = UserProfile.objects.get(id=user_id)
        if not user.is_student:
            raise serializers.ValidationError({'detail': '你不是学生！不能提交题目选项'})
        student = user.student
        question = validated_data.get('question')
        homework = question.homework
        if question.question_type!='QiTa':
            raise serializers.ValidationError({'detail':'该题不是其他题类型！不能添加其他类型的答案'})
        score = Score.objects.filter(student=student, schedule_lesson=homework.lesson_period.schedule_lesson)
        if not score:
            raise serializers.ValidationError({'detail': '你不是该课程的学生！不能创建代码答案'})
        if homework.limit_time < datetime.now():
            raise serializers.ValidationError({'detail': '该作业已过期！不能再提交'})
        homework_score = HomeworkScore.objects.filter(homework=homework, student=student)
        if not homework_score:
            raise serializers.ValidationError({'detail': '你还没有开始作业！不能提交'})
        if homework.timeout:
            homework_score = homework_score[0]
            over_time = homework_score.create_time + timedelta(hours=0, minutes=homework.timeout, seconds=0)
            if datetime.now() > over_time:
                raise serializers.ValidationError({'detail': '该作业已超出限定时间！不能再继续作业'})
        text_answer = validated_data.get('text_answer')
        student_other_answer=StudentOtherAnswer.objects.filter(question=question,student=student)
        if student_other_answer:
            raise serializers.ValidationError({'detail':'你已创建该题答案！不能再创建了'})
        student_other_answer=StudentOtherAnswer.objects.create(question=question,student=student,text_answer=text_answer)
        files=validated_data.get('file')
        if files:
            if len(files)>len(set(files)):
                raise serializers.ValidationError({'detail':'不能存在重复文件！'})
            for f in files:
                disk=f.disk
                if disk.ower_id!=user_id:
                    raise serializers.ValidationError({'detail':'你不能选择别人的网盘文件！'})
                if disk.if_close:
                    raise serializers.ValidationError({'detail':'你已经关闭了网盘，不能再继续使用网盘文件！'})
                if disk.if_disable:
                    raise serializers.ValidationError({'detail':'你的网盘已被禁用！不能再继续使用网盘文件'})
                if f.if_delete:
                    raise serializers.ValidationError({'detail':'该文件已被回收！不能再添加'})
                student_other_answer.file.add(f)
        student_other_answer.save()
        return student_other_answer

class StudentOtherAnswerUpdateSerializer(serializers.ModelSerializer):
    user_id = serializers.HiddenField(default=serializers.CurrentUserDefault())
    id = serializers.IntegerField(read_only=True)
    add_file_id_list = serializers.ListField(child=serializers.UUIDField(), required=False, allow_empty=True,
                                             allow_null=True, label='添加的文件的id列表', help_text='添加的文件的id列表',
                                             write_only=True)
    remove_file_id_list = serializers.ListField(child=serializers.UUIDField(), required=False, allow_empty=True,
                                                allow_null=True, label='删除的文件的id列表', help_text='删除的文件的id列表',
                                                write_only=True)

    class Meta:
        model = StudentOtherAnswer
        fields = ['text_answer', 'user_id', 'id', 'add_file_id_list', 'remove_file_id_list']
    def update(self, instance, validated_data):
        user_id = validated_data.get('user_id')
        user = UserProfile.objects.get(id=user_id)
        if not user.is_student:
            raise serializers.ValidationError({'detail': '你不是学生！不能提交题目选项'})
        student = user.student
        question = instance.question
        homework = question.homework
        if homework.limit_time < datetime.now():
            raise serializers.ValidationError({'detail': '该作业已过期！不能再提交'})
        homework_score = HomeworkScore.objects.filter(homework=homework, student=student)
        if not homework_score:
            raise serializers.ValidationError({'detail': '你还没有开始作业！不能提交'})
        homework_score = homework_score[0]
        if homework_score.if_submit:
            if not question.if_answer_update:
                raise serializers.ValidationError({'detail':'你已经提交了作业！不能再更改'})
        if homework.timeout:
            over_time = homework_score.create_time + timedelta(hours=0, minutes=homework.timeout, seconds=0)
            if datetime.now() > over_time:
                raise serializers.ValidationError({'detail': '该作业已超出限定时间！不能再继续作业'})
        instance.text_answer=validated_data.get('text_answer',instance.text_answer)
        remove_file_id_list = validated_data.get('remove_file_id_list')
        if remove_file_id_list:
            if len(remove_file_id_list) > len(set(remove_file_id_list)):
                raise serializers.ValidationError({'detail': '删除的文件重复！'})
            for id in remove_file_id_list:
                file = File.objects.filter(id=id)
                if file:
                    file = file[0]
                    try:
                        instance.file.remove(file)
                    except:
                        raise serializers.ValidationError({'detail': '该文件未添加！不能删除'})
                else:
                    raise serializers.ValidationError({'detail': '删除的文件不存在！'})
        add_file_id_list = validated_data.get('add_file_id_list')
        if add_file_id_list:
            if len(add_file_id_list) > len(set(add_file_id_list)):
                raise serializers.ValidationError({'detail': '添加的文件重复！'})
            for id in add_file_id_list:
                file = File.objects.filter(id=id)
                if file:
                    file = file[0]
                    disk = file.disk
                    if disk.ower_id != user_id:
                        raise serializers.ValidationError({'detail': '你不能选择别人的网盘文件！'})
                    if disk.if_close:
                        raise serializers.ValidationError({'detail': '你已经关闭了网盘，不能再继续使用网盘文件！'})
                    if disk.if_disable:
                        raise serializers.ValidationError({'detail': '你的网盘已被禁用！不能再继续使用网盘文件'})
                    if file.if_delete:
                        raise serializers.ValidationError({'detail': '该文件已被回收！不能再添加'})
                    try:
                        instance.file.add(file)
                    except:
                        raise serializers.ValidationError({'detail': '文件已存在！不能再添加'})
                else:
                    raise serializers.ValidationError({'detail': '添加的文件不存在！'})
        try:
            instance.save()
            return instance
        except:
            raise serializers.ValidationError({'detail': '文件输入有误！'})

class DaiMaFileListSerializer(serializers.ModelSerializer):
    class Meta:
        model=DaiMaFile
        fields='__all__'

class DaiMaFileCreateSerializer(serializers.ModelSerializer):
    user_id = serializers.HiddenField(default=serializers.CurrentUserDefault())
    id = serializers.IntegerField(read_only=True)
    class Meta:
        model=DaiMaFile
        fields=['user_id','id','question','daima_type','name']
    def create(self, validated_data):
        user_id = validated_data.get('user_id')
        user = UserProfile.objects.get(id=user_id)
        if not user.is_teacher:
            raise serializers.ValidationError({'detail': '你不是教师！不能创建代码文件'})
        teacher = user.teacher
        question = validated_data.get('question')
        if teacher != question.homework.lesson_period.schedule_lesson.teacher:
            raise serializers.ValidationError({'detail': '你不是该课程的教师！不能添加代码文件'})
        if question.question_type != 'DaiMa':
            raise serializers.ValidationError({'detail': '该题不是代码类型的题目！不能添加代码文件！'})
        name=validated_data.get('name')
        daima_file=DaiMaFile.objects.filter(question=question,name=name)
        if daima_file:
            raise serializers.ValidationError({'detail':'该题已存在该名字的代码文件！不能重复添加'})
        daima_file=DaiMaFile.objects.create(question=question,name=name,daima_type=validated_data.get('daima_type'))
        return daima_file

class DaiMaFileUpdateSerializer(serializers.ModelSerializer):
    user_id = serializers.HiddenField(default=serializers.CurrentUserDefault())
    id = serializers.IntegerField(read_only=True)
    class Meta:
        model=DaiMaFile
        fields=['user_id','id','name','daima_type']
    def update(self, instance, validated_data):
        user_id = validated_data.get('user_id')
        user = UserProfile.objects.get(id=user_id)
        if not user.is_teacher:
            raise serializers.ValidationError({'detail': '你不是教师！不能更改代码文件'})
        teacher = user.teacher
        question = instance.question
        if teacher != question.homework.lesson_period.schedule_lesson.teacher:
            raise serializers.ValidationError({'detail': '你不是该课程的教师！不能更改代码文件'})
        instance.name=validated_data.get('name',instance.name)
        instance.daima_type=validated_data.get('daima_type',instance.daima_type)
        instance.save()
        return instance

class DaiMaAnswerListSerializer(serializers.ModelSerializer):
    class Meta:
        model=DaiMaAnswer
        fields='__all__'

class DaiMaAnswerCreateSerializer(serializers.ModelSerializer):
    user_id = serializers.HiddenField(default=serializers.CurrentUserDefault())
    id = serializers.IntegerField(read_only=True)
    class Meta:
        model=DaiMaAnswer
        fields=['user_id','id','daima_type','daima_file','answer']
    def create(self, validated_data):
        user_id = validated_data.get('user_id')
        user = UserProfile.objects.get(id=user_id)
        if not user.is_teacher:
            raise serializers.ValidationError({'detail': '你不是教师！不能创建代码答案'})
        teacher = user.teacher
        daima_file=validated_data.get('daima_file')
        question = daima_file.question
        if teacher != question.homework.lesson_period.schedule_lesson.teacher:
            raise serializers.ValidationError({'detail': '你不是该课程的教师！不能添加代码答案'})
        daima_type=validated_data.get('daima_type')
        if daima_type!=daima_file.daima_type:
            if daima_file.daima_type!='不限':
                raise serializers.ValidationError({'detail':'该代码文件以限定代码类型！你不能更改'})
        daima_answer = DaiMaAnswer.objects.filter(daima_file=daima_file)
        if daima_answer:
            raise serializers.ValidationError({'detail':'你已创建该代码答案！不能重复创建'})
        daima_answer=DaiMaAnswer.objects.create(daima_type=daima_type,daima_file=daima_file,answer=validated_data.get('answer'))
        return daima_answer

class DaiMaAnswerUpdateSerializer(serializers.ModelSerializer):
    user_id = serializers.HiddenField(default=serializers.CurrentUserDefault())
    id = serializers.IntegerField(read_only=True)
    class Meta:
        model=DaiMaAnswer
        fields=['user_id','id','daima_type','answer']
    def update(self, instance, validated_data):
        user_id = validated_data.get('user_id')
        user = UserProfile.objects.get(id=user_id)
        if not user.is_teacher:
            raise serializers.ValidationError({'detail': '你不是教师！不能添加创建代码文件'})
        teacher = user.teacher
        daima_file = instance.daima_file
        question = daima_file.question
        if teacher != question.homework.lesson_period.schedule_lesson.teacher:
            raise serializers.ValidationError({'detail': '你不是该课程的教师！不能添加代码文件'})
        daima_type = validated_data.get('daima_type')
        if daima_type:
            if daima_type != daima_file.daima_type:
                if daima_file.daima_type != '不限':
                    raise serializers.ValidationError({'detail': '该代码文件以限定代码类型！你不能更改'})
            instance.daima_type=daima_type
        instance.answer=validated_data.get('answer',instance.answer)
        instance.save()
        return instance

class StudentDaiMaAnswerListSerializer(serializers.ModelSerializer):
    class Mete:
        model=StudentDaiMaAnswer
        fields='__all__'

class StudentDaiMaAnswerCreateSerializer(serializers.ModelSerializer):
    user_id = serializers.HiddenField(default=serializers.CurrentUserDefault())
    id = serializers.IntegerField(read_only=True)
    class Meta:
        model=StudentDaiMaAnswer
        fields=['user_id','id','daima_type','daima_file','answer','if_auto_submit']
    def create(self, validated_data):
        user_id = validated_data.get('user_id')
        user = UserProfile.objects.get(id=user_id)
        if not user.is_student:
            raise serializers.ValidationError({'detail': '你不是学生！不能创建代码答案'})
        student = user.student
        daima_file = validated_data.get('daima_file')
        question = daima_file.question
        homework = question.homework
        score = Score.objects.filter(student=student, schedule_lesson=homework.lesson_period.schedule_lesson)
        if not score:
            raise serializers.ValidationError({'detail': '你不是该课程的学生！不能创建代码答案'})
        if homework.limit_time < datetime.now():
            raise serializers.ValidationError({'detail': '该作业已过期！不能再提交'})
        homework_score = HomeworkScore.objects.filter(homework=homework, student=student)
        if not homework_score:
            raise serializers.ValidationError({'detail': '你还没有开始作业！不能提交'})
        if homework.timeout:
            homework_score = homework_score[0]
            over_time = homework_score.create_time + timedelta(hours=0, minutes=homework.timeout, seconds=0)
            if datetime.now() > over_time:
                raise serializers.ValidationError({'detail': '该作业已超出限定时间！不能再继续作业'})
        daima_type = validated_data.get('daima_type')
        if daima_type != daima_file.daima_type:
            if daima_file.daima_type != '不限':
                raise serializers.ValidationError({'detail': '该代码文件以限定代码类型！你不能更改'})
        student_daima_answer = StudentDaiMaAnswer.objects.filter(daima_file=daima_file,student=student)
        if student_daima_answer:
            raise serializers.ValidationError({'detail': '你已创建该代码文件答案！不能重复创建'})
        student_daima_answer = StudentDaiMaAnswer.objects.create(daima_type=daima_type, daima_file=daima_file,answer=validated_data.get('answer'),student=student,if_auto_submit=validated_data.get('if_auto_submit'))
        return student_daima_answer

class StudentDaiMaAnswerUpdateSerializer(serializers.ModelSerializer):
    user_id = serializers.HiddenField(default=serializers.CurrentUserDefault())
    id = serializers.IntegerField(read_only=True)
    class Meta:
        model=StudentDaiMaAnswer
        fields=['user_id','id','daima_type','answer']
    def update(self, instance, validated_data):
        user_id = validated_data.get('user_id')
        user = UserProfile.objects.get(id=user_id)
        if not user.is_student:
            raise serializers.ValidationError({'detail': '你不是学生！不能创建代码答案'})
        student = user.student
        question = instance.daima_file.question
        homework = question.homework
        if homework.limit_time < datetime.now():
            raise serializers.ValidationError({'detail': '该作业已过期！不能再提交'})
        homework_score = HomeworkScore.objects.filter(homework=homework, student=student)
        if not homework_score:
            raise serializers.ValidationError({'detail': '你还没有开始作业！不能提交'})
        homework_score = homework_score[0]
        if homework_score.if_submit:
            if not question.if_answer_update:
                raise serializers.ValidationError({'detail': '你已经提交了作业！不能再更改'})
        if homework.timeout:
            over_time = homework_score.create_time + timedelta(hours=0, minutes=homework.timeout, seconds=0)
            if datetime.now() > over_time:
                raise serializers.ValidationError({'detail': '该作业已超出限定时间！不能再继续作业'})
        daima_file = instance.daima_file
        if instance.student!=student:
            raise serializers.ValidationError({'detail': '你不能更改别人的代码答案！'})
        if not instance.if_auto_submit:
            raise serializers.ValidationError({'你不能更改该代码！'})
        daima_type = validated_data.get('daima_type')
        if daima_type:
            if daima_type != daima_file.daima_type:
                if daima_file.daima_type != '不限':
                    raise serializers.ValidationError({'detail': '该代码文件以限定代码类型！你不能更改'})
            instance.daima_type=daima_type
        instance.answer=validated_data.get('answer',instance.answer)
        instance.save()
        return instance

class QuestionScoreListSerializer(serializers.ModelSerializer):
    class Meta:
        model=QuestionScore
        fields='__all__'

class QuestionScoreCreateSerializer(serializers.ModelSerializer):
    user_id = serializers.HiddenField(default=serializers.CurrentUserDefault())
    id = serializers.IntegerField(read_only=True)
    score=serializers.FloatField(min_value=0.0,label='单题得分',help_text='单题得分')
    class Meta:
        model=QuestionScore
        fields=['user_id','id','student','question','score']
    def create(self, validated_data):
        user_id = validated_data.get('user_id')
        user = UserProfile.objects.get(id=user_id)
        if not user.is_teacher:
            raise serializers.ValidationError({'detail': '你不是教师！不能创建代码答案'})
        teacher = user.teacher
        question = validated_data.get('question')
        homework=question.homework
        schedule_lesson=homework.lesson_period.schedule_lesson
        if teacher != schedule_lesson.teacher:
            raise serializers.ValidationError({'detail': '你不是该课程的教师！不能批改作业'})
        student=validated_data.get('student')
        student_score=Score.objects.filter(student=student,schedule_lesson=schedule_lesson)
        if not student_score:
            raise serializers.ValidationError({'detail':'该学生不是该班级的学生！'})
        question_score=QuestionScore.objects.filter(student=student,question=question)
        if question_score:
            raise serializers.ValidationError({'detail':'该题已批改！不能再批改！你可以修改'})
        if homework.limit_time>datetime.now():
            raise serializers.ValidationError({'detail':'还未到时间！不能批改'})
        score=validated_data.get('score')
        if score>question.score:
            raise serializers.ValidationError({'detail':'分数不能超过该题总分！'})
        question_score = QuestionScore.objects.create(student=student, question=question,score=score)
        homework_score=HomeworkScore.objects.filter(homework=homework,student=student)
        if not homework_score:
            homework_score = HomeworkScore.objects.create(homework=homework, student=student)
        else:
            homework_score=homework_score[0]
        homework_score.total_score+=score
        homework_score.save()
        return question_score

class QuestionScoreUpdateSerializer(serializers.ModelSerializer):
    user_id = serializers.HiddenField(default=serializers.CurrentUserDefault())
    id = serializers.IntegerField(read_only=True)
    score = serializers.FloatField(min_value=0.0, label='单题得分', help_text='单题得分')
    class Meta:
        model = QuestionScore
        fields = ['user_id', 'id', 'score']
    def update(self, instance, validated_data):
        user_id = validated_data.get('user_id')
        user = UserProfile.objects.get(id=user_id)
        if not user.is_teacher:
            raise serializers.ValidationError({'detail': '你不是教师！不能创建代码答案'})
        teacher = user.teacher
        question = instance.question
        schedule_lesson = question.homework.lesson_period.schedule_lesson
        if teacher != schedule_lesson.teacher:
            raise serializers.ValidationError({'detail': '你不是该课程的教师！不能批改作业'})
        homework_score = HomeworkScore.objects.filter(homework=question.homework, student=instance.student)
        score=validated_data.get('score')
        if score>question.score:
            raise serializers.ValidationError({'detail':'分数不能超过该题总分！'})
        homework_score.total_score -= instance.score
        instance.score=score
        instance.save()
        homework_score.total_score += score
        homework_score.save()
        return instance

class AutoCorrectNoSubmitHomeworkSerialier(serializers.ModelSerializer):
    user_id = serializers.HiddenField(default=serializers.CurrentUserDefault())
    homework_id=serializers.IntegerField(min_value=0,label='作业id',help_text='作业id',write_only=True)
    class Meta:
        model=Homework
        fields=['homework_id','user_id']
    def create(self, validated_data):
        user_id = validated_data.get('user_id')
        user = UserProfile.objects.get(id=user_id)
        if not user.is_teacher:
            raise serializers.ValidationError({'detail': '你不是教师！不能操作！'})
        teacher = user.teacher
        homework_id = validated_data.get('homework_id')
        homework = Homework.objects.filter(id=homework_id)
        if not homework:
            raise serializers.ValidationError({'detail':'该作业不存在！'})
        homework=homework[0]
        schedule_lesson = homework.lesson_period.schedule_lesson
        if teacher != schedule_lesson.teacher:
            raise serializers.ValidationError({'detail': '你不是该课程的教师！不能批改该作业'})
        if homework.limit_time>datetime.now():
            raise serializers.ValidationError({'detail':'还未到时间！不能批改'})
        return homework

