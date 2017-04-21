# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rtg', '0010_auto_20160329_2328'),
    ]

    operations = [
        migrations.AlterField(
            model_name='extrabet',
            name='result_bet',
            field=models.CharField(max_length=50, blank=True),
        ),
    ]
