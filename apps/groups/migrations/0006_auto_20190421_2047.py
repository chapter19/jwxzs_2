# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2019-04-21 20:47
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('groups', '0005_defgroup_defgroupmember'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='defgroupmember',
            unique_together=set([('member', 'def_group')]),
        ),
    ]
