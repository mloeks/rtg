# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rtg', '0006_auto_20160328_2301'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gamebetresult',
            name='type',
            field=models.CharField(unique=True, max_length=50),
        ),
    ]
