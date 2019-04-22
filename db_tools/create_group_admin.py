import os,django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "jwxzs_2.settings")# project_name 项目名称
django.setup()

from users.models import Student,Teacher,UserProfile
from jwxzs_2.settings import PUBLIC_PASSWORD

from groups.models import Group,GroupAdministrator
from lessons.models import ScheduleLesson
from users.models import Class,Colloge,Teacher


def create_lesson_schedule():
    sl=ScheduleLesson.objects.all()
    for s in sl:
        group=Group()
        group.group_id=str(s.id)
        group.group_type=1
        group.group_name=str(s.lesson.name)+' '+str(s.class_name)
        try:
            group.save()
        except:
            pass
        admin = GroupAdministrator()
        try:
            admin.admin = s.teacher.user
        except:
            print(s.teacher)
        admin.group = group
        admin.if_super = True
        try:
            admin.save()
        except:
            pass


def create_class():
    cla=Class.objects.all()
    for cl in cla:
        group=Group()
        group.group_id=cl.id
        group.group_type=2
        group.group_name=str(cl.name)
        group.save()


def create_colloge():
    collo=Colloge.objects.all()
    for co in collo:
        group=Group()
        group.group_type=3
        group.group_id=co.id
        group.group_name=str(co.name)
        group.save()


def get_teacher_user():
    teach=Teacher.objects.all()
    for tea in teach:
        if tea.user:
            pass
        else:
            print(tea.id,tea.name)


if __name__ == '__main__':
    # create_lesson_schedule()
    # get_teacher_user()
    create_class()
    create_colloge()








