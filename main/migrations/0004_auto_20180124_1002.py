# -*- coding: utf-8 -*-
# Generated by Django 1.11.9 on 2018-01-24 09:02
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_auto_20171112_2104'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bettable',
            name='name',
            field=models.CharField(max_length=50),
        ),
    ]
