# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2019-06-15 00:09
from __future__ import unicode_literals

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('disks', '0017_auto_20190614_2345'),
    ]

    operations = [
        migrations.AlterField(
            model_name='file',
            name='id',
            field=models.UUIDField(default=uuid.UUID('0cbcbdf2-3114-4405-9ca2-44bdf305047c'), primary_key=True, serialize=False, verbose_name='id'),
        ),
        migrations.AlterField(
            model_name='file',
            name='verbose_id',
            field=models.UUIDField(default=uuid.UUID('02b90eee-cfb9-412c-b576-8aaddc8794e8'), verbose_name='用于下载的id'),
        ),
        migrations.AlterField(
            model_name='fileextension',
            name='id',
            field=models.UUIDField(default=uuid.UUID('9c29b34d-b25a-4601-8f5f-bf6ed87502ed'), primary_key=True, serialize=False, verbose_name='id'),
        ),
        migrations.AlterField(
            model_name='folder',
            name='id',
            field=models.UUIDField(default=uuid.UUID('48dd338f-0bc4-4157-b6d6-79c2f638ff49'), primary_key=True, serialize=False, verbose_name='id'),
        ),
        migrations.AlterField(
            model_name='sharelink',
            name='id',
            field=models.UUIDField(default=uuid.UUID('3497455f-653e-4ca1-8cf7-bd8d7a349a00'), primary_key=True, serialize=False, verbose_name='id'),
        ),
        migrations.AlterField(
            model_name='sharelinkfile',
            name='id',
            field=models.UUIDField(default=uuid.UUID('0e3f0175-c7e0-438a-8574-1711e5be0499'), primary_key=True, serialize=False, verbose_name='id'),
        ),
        migrations.AlterField(
            model_name='sharelinkfile',
            name='verbose_id',
            field=models.UUIDField(default=uuid.UUID('c2542c1f-ed5f-4d44-96f1-b5cf354a5a82'), verbose_name='用于下载的id'),
        ),
        migrations.AlterField(
            model_name='sharelinkfolder',
            name='id',
            field=models.UUIDField(default=uuid.UUID('4e4c6960-9409-4500-89bf-67d19dd9eb72'), primary_key=True, serialize=False, verbose_name='id'),
        ),
    ]
