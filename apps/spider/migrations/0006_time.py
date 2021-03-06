# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2019-06-15 20:21
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('spider', '0005_auto_20190615_2014'),
    ]

    operations = [
        migrations.CreateModel(
            name='Time',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('hours', models.IntegerField(default=2, verbose_name='几小时更新')),
                ('type', models.CharField(choices=[('Redio', '教务通知'), ('TeacherPhoto', '教师照片'), ('StudentPhoto', '学生照片')], default='Redio', max_length=18, verbose_name='定时更新器类型')),
            ],
            options={
                'verbose_name': '自动更新时间',
                'verbose_name_plural': '自动更新时间',
            },
        ),
    ]
