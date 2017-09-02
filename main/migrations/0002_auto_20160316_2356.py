# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='game',
            old_name='result_awaygoals',
            new_name='awaygoals',
        ),
        migrations.RenameField(
            model_name='game',
            old_name='result_homegoals',
            new_name='homegoals',
        ),
    ]
