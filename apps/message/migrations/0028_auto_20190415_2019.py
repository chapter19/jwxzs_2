# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2019-04-15 20:19
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('message', '0027_receivergroup_add_time'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='groupreceivermessage',
            options={'verbose_name': '接收组接收人消息', 'verbose_name_plural': '接收组接收人消息'},
        ),
        migrations.AlterField(
            model_name='receivergroup',
            name='group_name',
            field=models.CharField(blank=True, default='', max_length=60, null=True, verbose_name='组织名'),
        ),
    ]
