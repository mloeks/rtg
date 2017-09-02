# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0008_auto_20160329_2248'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='extrachoice',
            options={'ordering': ['sort_index']},
        ),
        migrations.AlterUniqueTogether(
            name='extrachoice',
            unique_together=set([('name', 'extra')]),
        ),
    ]
