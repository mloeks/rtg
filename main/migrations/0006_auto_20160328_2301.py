# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0005_auto_20160324_0007'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gamebetresult',
            name='points',
            field=models.SmallIntegerField(),
        ),
    ]
