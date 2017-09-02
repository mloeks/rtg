# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import main.utils
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Extra',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=50)),
                ('points', models.PositiveSmallIntegerField(default=10)),
                ('deadline', models.DateTimeField(null=True, blank=True)),
                ('result', models.CharField(max_length=50, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='ExtraBet',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('result_bet', models.CharField(max_length=50)),
                ('extra', models.ForeignKey(to='main.Extra')),
            ],
        ),
        migrations.CreateModel(
            name='ExtraChoice',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
                ('sort_index', models.CharField(max_length=10, blank=True)),
                ('extra', models.ForeignKey(to='main.Extra')),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Game',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('kickoff', models.DateTimeField()),
                ('deadline', models.DateTimeField(blank=True)),
                ('result_homegoals', models.SmallIntegerField(default=-1)),
                ('result_awaygoals', models.SmallIntegerField(default=-1)),
            ],
            options={
                'ordering': ['kickoff'],
            },
        ),
        migrations.CreateModel(
            name='GameBet',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('homegoals', models.SmallIntegerField(default=-1)),
                ('awaygoals', models.SmallIntegerField(default=-1)),
                ('game', models.ForeignKey(to='main.Game')),
            ],
        ),
        migrations.CreateModel(
            name='GameBetResult',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('type', models.CharField(max_length=50)),
                ('points', models.IntegerField()),
                ('sort_id', models.CharField(max_length=5)),
            ],
            options={
                'ordering': ['sort_id'],
            },
        ),
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('content', models.TextField()),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('sticky', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('avatar', models.ImageField(storage=main.storage.OverwriteStorage(), null=True, upload_to=main.utils.get_avatar_path, blank=True)),
                ('avatar_cropped', models.ImageField(storage=main.storage.OverwriteStorage(), null=True, upload_to=main.utils.get_thumb_path, blank=True)),
                ('location', models.CharField(max_length=50, blank=True)),
                ('location_lat', models.FloatField(null=True, blank=True)),
                ('location_lon', models.FloatField(null=True, blank=True)),
                ('current_rank', models.PositiveSmallIntegerField(default=1)),
                ('current_display_rank', models.PositiveSmallIntegerField(default=1)),
                ('royal_connection', models.CharField(max_length=20, blank=True)),
                ('royal_connection_person', models.CharField(max_length=50, blank=True)),
                ('has_paid', models.BooleanField(default=False)),
                ('reminder_emails', models.BooleanField(default=True)),
                ('daily_emails', models.BooleanField(default=True)),
                ('about', models.CharField(max_length=500, null=True, blank=True)),
                ('rank_history', models.CharField(max_length=500, null=True, blank=True)),
                ('user', models.OneToOneField(primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['user'],
            },
        ),
        migrations.CreateModel(
            name='Team',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=50)),
                ('abbreviation', models.CharField(unique=True, max_length=3)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='TournamentGroup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=20)),
                ('abbreviation', models.CharField(unique=True, max_length=3)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='TournamentRound',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=50)),
                ('is_knock_out', models.BooleanField(default=False)),
                ('display_order', models.PositiveSmallIntegerField()),
                ('abbreviation', models.CharField(max_length=3, blank=True)),
            ],
            options={
                'ordering': ['display_order'],
            },
        ),
        migrations.CreateModel(
            name='Venue',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=50)),
                ('city', models.CharField(max_length=50)),
                ('capacity', models.PositiveIntegerField(blank=True)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.AddField(
            model_name='team',
            name='group',
            field=models.ForeignKey(to='main.TournamentGroup'),
        ),
        migrations.AddField(
            model_name='post',
            name='author',
            field=models.ForeignKey(related_name='authored_posts', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='post',
            name='parent_post',
            field=models.ForeignKey(related_name='child_posts', blank=True, to='main.Post', null=True),
        ),
        migrations.AddField(
            model_name='post',
            name='target_user',
            field=models.ForeignKey(related_name='targeted_posts', blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='post',
            name='users_disliked',
            field=models.ManyToManyField(related_name='disliked_posts', to=settings.AUTH_USER_MODEL, blank=True),
        ),
        migrations.AddField(
            model_name='post',
            name='users_liked',
            field=models.ManyToManyField(related_name='liked_posts', to=settings.AUTH_USER_MODEL, blank=True),
        ),
        migrations.AddField(
            model_name='gamebet',
            name='result_bet_type',
            field=models.ForeignKey(verbose_name=b'Result Type', blank=True, to='main.GameBetResult', null=True),
        ),
        migrations.AddField(
            model_name='gamebet',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='game',
            name='awayteam',
            field=models.ForeignKey(related_name='games_away', to='main.Team'),
        ),
        migrations.AddField(
            model_name='game',
            name='hometeam',
            field=models.ForeignKey(related_name='games_home', to='main.Team'),
        ),
        migrations.AddField(
            model_name='game',
            name='round',
            field=models.ForeignKey(to='main.TournamentRound'),
        ),
        migrations.AddField(
            model_name='game',
            name='venue',
            field=models.ForeignKey(to='main.Venue'),
        ),
        migrations.AddField(
            model_name='extrabet',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='extra',
            name='game_yield',
            field=models.ForeignKey(blank=True, to='main.Game', null=True),
        ),
        migrations.AlterUniqueTogether(
            name='gamebet',
            unique_together=set([('game', 'user')]),
        ),
    ]
