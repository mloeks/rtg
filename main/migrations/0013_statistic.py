# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
        ('main', '0012_auto_20160330_1815'),
    ]

    operations = [
        migrations.CreateModel(
            name='Statistic',
            fields=[
                ('user', models.OneToOneField(primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('no_bets', models.PositiveSmallIntegerField(default=0)),
                ('no_volltreffer', models.PositiveSmallIntegerField(default=0)),
                ('points', models.PositiveSmallIntegerField(default=0)),
            ],
        ),
    ]
