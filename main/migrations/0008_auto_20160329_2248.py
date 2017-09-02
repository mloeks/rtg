# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0007_auto_20160328_2302'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='extra',
            name='game_yield',
        ),
        migrations.RemoveField(
            model_name='profile',
            name='royal_connection',
        ),
        migrations.RemoveField(
            model_name='profile',
            name='royal_connection_person',
        ),
        migrations.AlterField(
            model_name='extra',
            name='deadline',
            field=models.DateTimeField(default='2016-04-04 18:00:00+0000'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='extra',
            name='points',
            field=models.SmallIntegerField(default=10),
        ),
    ]
