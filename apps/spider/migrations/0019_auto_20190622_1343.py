# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2019-06-22 13:43
from __future__ import unicode_literals

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('spider', '0018_auto_20190621_2127'),
    ]

    operations = [
        migrations.AlterField(
            model_name='spiderlog',
            name='verbose_id',
            field=models.UUIDField(default=uuid.UUID('7ea76684-1148-4e7d-8dd7-98413860a752'), verbose_name='第二个的id'),
        ),
    ]
