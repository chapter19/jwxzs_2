# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2019-06-17 09:35
from __future__ import unicode_literals

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('disks', '0029_auto_20190617_0931'),
    ]

    operations = [
        migrations.AlterField(
            model_name='file',
            name='id',
            field=models.UUIDField(default=uuid.UUID('a63919d8-04f0-4e04-a961-7a59d2893947'), primary_key=True, serialize=False, verbose_name='id'),
        ),
        migrations.AlterField(
            model_name='file',
            name='verbose_id',
            field=models.UUIDField(default=uuid.UUID('fb96f527-8a1b-4591-ba0c-25e7653df16f'), verbose_name='用于下载的id'),
        ),
        migrations.AlterField(
            model_name='fileextension',
            name='id',
            field=models.UUIDField(default=uuid.UUID('ec58e345-3714-46c0-a573-4f4c6ed02664'), primary_key=True, serialize=False, verbose_name='id'),
        ),
        migrations.AlterField(
            model_name='folder',
            name='id',
            field=models.UUIDField(default=uuid.UUID('089a0477-99a3-4a33-8f7d-fbf13476dae4'), primary_key=True, serialize=False, verbose_name='id'),
        ),
        migrations.AlterField(
            model_name='sharelink',
            name='id',
            field=models.UUIDField(default=uuid.UUID('a8cd2682-62ac-49a4-9a53-063e7e7a0881'), primary_key=True, serialize=False, verbose_name='id'),
        ),
        migrations.AlterField(
            model_name='sharelinkfile',
            name='id',
            field=models.UUIDField(default=uuid.UUID('71e2e579-02cf-420b-bd25-1475280a4eae'), primary_key=True, serialize=False, verbose_name='id'),
        ),
        migrations.AlterField(
            model_name='sharelinkfile',
            name='verbose_id',
            field=models.UUIDField(default=uuid.UUID('019ebbda-82df-4637-9aa3-9e05b3156d09'), verbose_name='用于下载的id'),
        ),
        migrations.AlterField(
            model_name='sharelinkfolder',
            name='id',
            field=models.UUIDField(default=uuid.UUID('97743352-a947-4c20-8f0a-529abe191a75'), primary_key=True, serialize=False, verbose_name='id'),
        ),
    ]
