# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2019-04-16 21:48
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('semesters', '0002_auto_20190416_2134'),
    ]

    operations = [
        migrations.RenameField(
            model_name='semester',
            old_name='if_spider',
            new_name='if_spider_semester',
        ),
        migrations.AddField(
            model_name='semester',
            name='if_spider_grade',
            field=models.BooleanField(default=False, verbose_name='是否爬取该年级'),
        ),
    ]
