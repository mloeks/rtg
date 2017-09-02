# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0019_merge'),
    ]

    operations = [
        migrations.AddField(
            model_name='statistic',
            name='no_differenz',
            field=models.PositiveSmallIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='statistic',
            name='no_niete',
            field=models.PositiveSmallIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='statistic',
            name='no_remis_tendenz',
            field=models.PositiveSmallIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='statistic',
            name='no_tendenz',
            field=models.PositiveSmallIntegerField(default=0),
        ),
    ]
