# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2019-04-15 21:53
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('message', '0029_auto_20190415_2020'),
    ]

    operations = [
        migrations.AlterField(
            model_name='message',
            name='type',
            field=models.IntegerField(choices=[(1, '系统通知'), (2, '作业通知'), (3, '普通消息'), (4, '教务通知'), (5, '通知回复')], default=3, verbose_name='消息类型'),
        ),
    ]
