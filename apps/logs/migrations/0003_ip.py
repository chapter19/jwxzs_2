# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2019-05-04 17:25
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('logs', '0002_auto_20190504_1716'),
    ]

    operations = [
        migrations.CreateModel(
            name='Ip',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ip', models.GenericIPAddressField(default='', verbose_name='ip')),
                ('address', models.CharField(blank=True, default='', max_length=100, null=True, verbose_name='地址')),
            ],
            options={
                'verbose_name': 'IP和地址',
                'verbose_name_plural': 'IP和地址',
            },
        ),
    ]
