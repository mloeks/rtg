# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0011_auto_20160329_2333'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='post',
            name='target_user',
        ),
        migrations.RemoveField(
            model_name='post',
            name='users_disliked',
        ),
        migrations.RemoveField(
            model_name='post',
            name='users_liked',
        ),
    ]
