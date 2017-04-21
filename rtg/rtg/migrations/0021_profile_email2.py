# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rtg', '0020_auto_20160522_1335'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='email2',
            field=models.EmailField(max_length=254, blank=True),
        ),
    ]
