# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0016_post_finished'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='post',
            name='parent_post',
        ),
        migrations.RemoveField(
            model_name='post',
            name='sticky',
        ),
        migrations.AddField(
            model_name='post',
            name='as_mail',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='post',
            name='force_mail',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='post',
            name='news_appear',
            field=models.BooleanField(default=True),
        ),
    ]
