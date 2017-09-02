# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0013_statistic'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='extrachoice',
            options={'ordering': ['sort_index', 'name']},
        ),
        migrations.AlterField(
            model_name='extrachoice',
            name='extra',
            field=models.ForeignKey(related_name='choices', to='main.Extra'),
        ),
    ]
