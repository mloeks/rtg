# -*- coding: utf-8 -*-
# Generated by Django 1.11.9 on 2018-06-07 21:18
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0016_auto_20180605_2314'),
    ]

    operations = [
        migrations.AddField(
            model_name='game',
            name='openligadb_match_id',
            field=models.TextField(blank=True, null=True),
        ),
    ]
