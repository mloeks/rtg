# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-11-12 20:03
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bettable',
            name='result',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
