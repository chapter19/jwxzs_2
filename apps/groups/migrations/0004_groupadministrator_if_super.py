# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2019-04-20 20:53
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('groups', '0003_auto_20190420_2021'),
    ]

    operations = [
        migrations.AddField(
            model_name='groupadministrator',
            name='if_super',
            field=models.BooleanField(default=False, verbose_name='是否为超级管理员'),
        ),
    ]
