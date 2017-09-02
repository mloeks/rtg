# -*- coding: utf-8 -*-

from random import choice, randrange
from string import ascii_uppercase

from django.contrib.auth.models import User
from django.utils import timezone

from main.models import TournamentGroup, TournamentRound, Game, Venue, Team, GameBet, GameBetResult, Extra, ExtraChoice, \
    ExtraBet, Post


class TestModelUtils:

    @staticmethod
    def cleanup():
        # with transaction.atomic():
        #     Game.objects.all().delete()
        # with transaction.atomic():
        #     Venue.objects.all().delete()
        # with transaction.atomic():
        #     TournamentRound.objects.all().delete()
        # with transaction.atomic():
        #     TournamentGroup.objects.all().delete()
        # with transaction.atomic():
        #     Team.objects.all().delete()
        pass

    @staticmethod
    def create_user(username=None, first_name=None, last_name=None):
        username = username or TestModelUtils.create_random_string(8)
        first_name = first_name or TestModelUtils.create_random_string(8)
        last_name = last_name or TestModelUtils.create_random_string(8)

        return User.objects.create(username=username, first_name=first_name, last_name=last_name)

    @staticmethod
    def create_game(hometeam=None, awayteam=None, kickoff=None, deadline=None, venue=None, round=None, homegoals=-1, awaygoals=-1):
        hometeam = hometeam or TestModelUtils.create_team()
        awayteam = awayteam or TestModelUtils.create_team()
        kickoff = kickoff or timezone.now()
        deadline = deadline or kickoff
        venue = venue or TestModelUtils.create_venue()
        round = round or TestModelUtils.create_round()

        return Game.objects.create(kickoff=kickoff, deadline=deadline, homegoals=homegoals, awaygoals=awaygoals,
                                   hometeam=hometeam, awayteam=awayteam, venue=venue, round=round)

    @staticmethod
    def create_gamebet(user=None, game=None, homegoals=-1, awaygoals=-1, result_bet_type=None):
        user = user or TestModelUtils.create_user()
        game = game or TestModelUtils.create_game()

        return GameBet.objects.create(user=user, game=game, homegoals=homegoals, awaygoals=awaygoals,
                                      result_bet_type=result_bet_type)

    @staticmethod
    def create_gamebet_result_types():
        GameBetResult.objects.create(type='volltreffer', points=5, sort_id='a')
        GameBetResult.objects.create(type='differenz', points=3, sort_id='b')
        GameBetResult.objects.create(type='remis-tendenz', points=2, sort_id='c')
        GameBetResult.objects.create(type='tendenz', points=1, sort_id='d')
        GameBetResult.objects.create(type='niete', points=0, sort_id='e')

    @staticmethod
    def create_venue(name=None, city=None, capacity=None):
        name = name or TestModelUtils.create_random_string()
        city = city or TestModelUtils.create_random_string()
        capacity = capacity or TestModelUtils.create_random_number(50000)

        return Venue.objects.create(name=name, city=city, capacity=capacity)

    @staticmethod
    def create_round(name=None, is_knock_out=False, display_order=None, abbreviation=None):
        name = name or TestModelUtils.create_random_string()
        display_order = display_order or TestModelUtils.create_random_number(100)
        abbreviation = abbreviation or name[:3]

        return TournamentRound.objects.create(name=name, is_knock_out=is_knock_out, display_order=display_order, abbreviation=abbreviation)

    @staticmethod
    def create_group(name=None, abbreviation=None):
        name = name or TestModelUtils.create_random_string()
        abbreviation = abbreviation or name[:3]

        return TournamentGroup.objects.create(name=name, abbreviation=abbreviation)

    @staticmethod
    def create_team(name=None, abbreviation=None, group=None):
        name = name or TestModelUtils.create_random_string()
        abbreviation = abbreviation or name[:3]
        group = group or TestModelUtils.create_group()

        return Team.objects.create(name=name, abbreviation=abbreviation, group=group)

    @staticmethod
    def create_extra(name=None, points=10, deadline=timezone.now(), result=''):
        name = name or TestModelUtils.create_random_string(6)

        return Extra.objects.create(name=name, points=points, deadline=deadline, result=result)

    @staticmethod
    def create_extrachoice(name=None, extra=None, sort_index=''):
        name = name or TestModelUtils.create_random_string(6)
        extra = extra or TestModelUtils.create_extra()

        return ExtraChoice.objects.create(name=name, extra=extra, sort_index=sort_index)

    @staticmethod
    def create_extrabet(result_bet='', extra=None, user=None):
        user = user or TestModelUtils.create_user()
        extra = extra or TestModelUtils.create_extra()

        return ExtraBet.objects.create(result_bet=result_bet, user=user, extra=extra)

    @staticmethod
    def create_post(content=None, author=None, parent_post=None, sticky=False):
        content = content or TestModelUtils.create_random_string(100)
        author = author or TestModelUtils.create_user()

        return Post.objects.create(content=content, author=author, parent_post=parent_post, sticky=sticky)

    @staticmethod
    def create_random_string(length=12):
        return ''.join(choice(ascii_uppercase) for i in range(length))

    @staticmethod
    def create_random_number(maxnr=1000):
        return randrange(maxnr)

    @staticmethod
    def create_datetime_from_now(timedelta=None):
        dt = timezone.now()
        if timedelta:
            dt = dt + timedelta
        return dt