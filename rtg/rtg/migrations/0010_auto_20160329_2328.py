# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rtg', '0009_auto_20160329_2321'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='extrabet',
            unique_together=set([('extra', 'user')]),
        ),
    ]
