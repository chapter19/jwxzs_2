# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2019-05-10 00:16
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lessons', '0014_majorlesson_limit_lesson_minimum_credit'),
        ('users', '0019_auto_20190509_1707'),
        ('semesters', '0003_nextsemester'),
        ('subject', '0010_myxuanke'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='steponelessonteacher',
            unique_together=set([('lesson', 'semester', 'teacher')]),
        ),
    ]
