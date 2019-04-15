# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2019-04-13 20:28
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('message', '0022_auto_20190413_1956'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='groupreceivermessage',
            name='group',
        ),
        migrations.RemoveField(
            model_name='messagefile',
            name='message',
        ),
        migrations.RemoveField(
            model_name='receivergroup',
            name='message',
        ),
        migrations.RemoveField(
            model_name='receivermessage',
            name='message',
        ),
        migrations.AddField(
            model_name='message',
            name='file',
            field=models.ManyToManyField(help_text='文件', related_name='message', to='message.MessageFile', verbose_name='文件'),
        ),
        migrations.AddField(
            model_name='message',
            name='message_receiver',
            field=models.ManyToManyField(help_text='接收人', related_name='message', to='message.ReceiverMessage', verbose_name='接收人'),
        ),
        migrations.AddField(
            model_name='message',
            name='message_receiver_group',
            field=models.ManyToManyField(help_text='接收组', related_name='message', to='message.ReceiverGroup', verbose_name='接收组'),
        ),
        migrations.AddField(
            model_name='receivergroup',
            name='message_receiver',
            field=models.ManyToManyField(related_name='receiver_group', to='message.GroupReceiverMessage', verbose_name='接收人'),
        ),
    ]
