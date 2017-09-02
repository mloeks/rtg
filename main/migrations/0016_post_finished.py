# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0015_post_title'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='finished',
            field=models.BooleanField(default=False),
        ),
    ]
