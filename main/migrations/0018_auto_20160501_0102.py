# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0017_auto_20160501_0032'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='finished',
            field=models.BooleanField(default=True),
        ),
    ]
