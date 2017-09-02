# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_auto_20160322_2335'),
    ]

    operations = [
        migrations.AlterField(
            model_name='venue',
            name='capacity',
            field=models.PositiveIntegerField(null=True, blank=True),
        ),
    ]
