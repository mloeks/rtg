# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rtg', '0014_auto_20160428_1958'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='title',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
    ]
