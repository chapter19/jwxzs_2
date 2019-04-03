# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2019-04-02 19:43
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('scores', '0005_remove_newscore_semester'),
    ]

    operations = [
        migrations.AddField(
            model_name='totalcredit',
            name='add_time',
            field=models.DateTimeField(default=datetime.datetime.now, verbose_name='添加时间'),
        ),
        migrations.AlterField(
            model_name='totalcredit',
            name='student',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.Student', verbose_name='学生'),
        ),
    ]
