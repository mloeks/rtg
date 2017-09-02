# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0004_auto_20160324_0000'),
    ]

    operations = [
        migrations.AlterField(
            model_name='game',
            name='deadline',
            field=models.DateTimeField(),
        ),
    ]
