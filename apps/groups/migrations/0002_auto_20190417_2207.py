# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2019-04-17 22:07
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('groups', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='group',
            name='group_type',
            field=models.IntegerField(choices=[(1, '课程班级'), (2, '班级'), (3, '学院'), (4, '专业'), (5, '自定义')], default=1, verbose_name='组织类型'),
        ),
    ]
