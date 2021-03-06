# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2019-06-10 08:48
from __future__ import unicode_literals

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('disks', '0009_auto_20190610_0824'),
    ]

    operations = [
        migrations.AlterField(
            model_name='file',
            name='id',
            field=models.UUIDField(default=uuid.UUID('f223fada-e832-4a37-a564-41b67dd73691'), primary_key=True, serialize=False, verbose_name='id'),
        ),
        migrations.AlterField(
            model_name='file',
            name='verbose_id',
            field=models.UUIDField(default=uuid.UUID('9b4aaa78-5c36-4803-b431-9488d2d800d7'), verbose_name='用于下载的id'),
        ),
        migrations.AlterField(
            model_name='fileextension',
            name='id',
            field=models.UUIDField(default=uuid.UUID('cfd0fa43-cf05-48a8-892b-2c4f883483ac'), primary_key=True, serialize=False, verbose_name='id'),
        ),
        migrations.AlterField(
            model_name='folder',
            name='id',
            field=models.UUIDField(default=uuid.UUID('c8820dac-c394-4e28-a780-8fba3c40d9e5'), primary_key=True, serialize=False, verbose_name='id'),
        ),
        migrations.AlterField(
            model_name='sharelink',
            name='id',
            field=models.UUIDField(default=uuid.UUID('84e74cda-f4c5-458b-866f-ed79f6654936'), primary_key=True, serialize=False, verbose_name='id'),
        ),
        migrations.AlterField(
            model_name='sharelinkfile',
            name='id',
            field=models.UUIDField(default=uuid.UUID('f91cb5bb-bf09-4f5d-a054-41da5efc8a1d'), primary_key=True, serialize=False, verbose_name='id'),
        ),
        migrations.AlterField(
            model_name='sharelinkfile',
            name='verbose_id',
            field=models.UUIDField(default=uuid.UUID('1e28e8c5-efc2-404a-9466-7bc545010954'), verbose_name='用于下载的id'),
        ),
        migrations.AlterField(
            model_name='sharelinkfolder',
            name='id',
            field=models.UUIDField(default=uuid.UUID('c5aae3a1-11bd-4559-8f1d-7a500d8d6e63'), primary_key=True, serialize=False, verbose_name='id'),
        ),
    ]
