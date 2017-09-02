# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_auto_20160316_2356'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='current_display_rank',
        ),
        migrations.RemoveField(
            model_name='profile',
            name='current_rank',
        ),
        migrations.RemoveField(
            model_name='profile',
            name='location_lat',
        ),
        migrations.RemoveField(
            model_name='profile',
            name='location_lon',
        ),
        migrations.RemoveField(
            model_name='profile',
            name='rank_history',
        ),
    ]
