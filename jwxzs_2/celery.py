#-*- coding:utf-8 -*-

from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab,timedelta

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jwxzs_2.settings')

app = Celery('jwxzs_2')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()



app.conf.update(
    CELERYBEAT_SCHEDULE = {
        'redio-spider-task': {
            'task': 'redio.tasks.get_redio',
            'schedule':  timedelta(hours=2),
        },
        'student-photo-task': {
            'task': 'users.tasks.student_photo_task',
            'schedule':  timedelta(hours=168),
        },
        'teacher-photo-task': {
            'task': 'users.tasks.teacher_photo_task',
            'schedule':  timedelta(hours=168),
        },
    }
)



@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))