#-*- coding:utf-8 -*-



from __future__ import absolute_import, unicode_literals

import os,django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "jwxzs_2.settings")# project_name 项目名称
django.setup()

# import os
from celery import Celery
from celery.schedules import crontab,timedelta


# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jwxzs_2.settings')

app = Celery('jwxzs_2',backend="redis://:1@127.0.0.1:6379/3")



# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

from spider.models import Timer

try:
    redio_timer_hours=Timer.objects.get(type='Redio').hours
except:
    redio_timer_hours=2

try:
    student_photo_timer_hours=Timer.objects.get(type='StudentPhoto').hours
except:
    student_photo_timer_hours=168

try:
    teacher_photo_timer_hours=Timer.objects.get(type='TeacherPhoto').hours
except:
    teacher_photo_timer_hours=168

app.conf.update(
    CELERYBEAT_SCHEDULE = {
        'redio-spider-task': {
            'task': 'redio.tasks.get_redio',
            'schedule':  timedelta(hours=redio_timer_hours),
        },
        'student-photo-task': {
            'task': 'users.tasks.student_photo_task',
            'schedule':  timedelta(hours=student_photo_timer_hours),
        },
        'teacher-photo-task': {
            'task': 'users.tasks.teacher_photo_task',
            'schedule':  timedelta(hours=teacher_photo_timer_hours),
        },
    },
    timezone = 'Asia/Shanghai',
    enable_utc = True,
)



@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))