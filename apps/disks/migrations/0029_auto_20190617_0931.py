# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2019-06-17 09:31
from __future__ import unicode_literals

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('disks', '0028_auto_20190617_0929'),
    ]

    operations = [
        migrations.AlterField(
            model_name='file',
            name='id',
            field=models.UUIDField(default=uuid.UUID('aa96a025-0200-45f2-8d62-70acc7754c7e'), primary_key=True, serialize=False, verbose_name='id'),
        ),
        migrations.AlterField(
            model_name='file',
            name='verbose_id',
            field=models.UUIDField(default=uuid.UUID('572f3beb-c233-458e-b556-cf5aacfde6f4'), verbose_name='用于下载的id'),
        ),
        migrations.AlterField(
            model_name='fileextension',
            name='id',
            field=models.UUIDField(default=uuid.UUID('31e8c284-fbf7-448b-8cdf-58a314628b83'), primary_key=True, serialize=False, verbose_name='id'),
        ),
        migrations.AlterField(
            model_name='folder',
            name='id',
            field=models.UUIDField(default=uuid.UUID('7835226a-7fe2-4cb5-a07d-2105e5e5b68a'), primary_key=True, serialize=False, verbose_name='id'),
        ),
        migrations.AlterField(
            model_name='sharelink',
            name='id',
            field=models.UUIDField(default=uuid.UUID('2c3a4ce0-7643-4f4d-9532-d9f63052ce60'), primary_key=True, serialize=False, verbose_name='id'),
        ),
        migrations.AlterField(
            model_name='sharelinkfile',
            name='id',
            field=models.UUIDField(default=uuid.UUID('94f99a73-da8e-481a-a1f3-8e41f5a45195'), primary_key=True, serialize=False, verbose_name='id'),
        ),
        migrations.AlterField(
            model_name='sharelinkfile',
            name='verbose_id',
            field=models.UUIDField(default=uuid.UUID('68a2a23f-782b-4bca-8c8e-8c5270ca1d4a'), verbose_name='用于下载的id'),
        ),
        migrations.AlterField(
            model_name='sharelinkfolder',
            name='id',
            field=models.UUIDField(default=uuid.UUID('f04056ba-a31d-4a06-ba52-5b355a246792'), primary_key=True, serialize=False, verbose_name='id'),
        ),
    ]
