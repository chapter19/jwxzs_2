# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-03-25 14:23
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('lessons', '0003_auto_20190325_0850'),
    ]

    operations = [
        migrations.AlterField(
            model_name='schedulelesson',
            name='teacher',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='users.Teacher', verbose_name='\u6559\u5e08'),
        ),
    ]
