# -*- coding: utf-8 -*-
# Generated by Django 1.11.9 on 2018-03-26 20:57
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0006_auto_20180322_2304'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='avatar_cropped',
        ),
    ]
