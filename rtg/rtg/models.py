# -*- coding: utf-8 -*-

from datetime import *

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models, utils
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.utils.translation import ugettext as _

from storage import OverwriteStorage
import utils
from validators import *


class TournamentGroup(models.Model):
    name = models.CharField(max_length=20, unique=True)
    abbreviation =models.CharField(max_length=3, unique=True)

    class Meta:
        ordering = ["name"]

    def __unicode__(self):  # Python 3: def __str__(self):
        return self.name


class TournamentRound(models.Model):
    name = models.CharField(max_length=50, unique=True)
    is_knock_out = models.BooleanField(default=False, blank=False)
    display_order = models.PositiveSmallIntegerField()
    abbreviation = models.CharField(max_length=3, blank=True)

    def get_all_games(self):
        return Game.objects.filter(round=self)

    @staticmethod
    # TODO DEPRECATED, UNTESTED: if required, re-implement in frontend
    def get_current_round():
        test_date = timezone.now() if not settings.FAKE_DATE else settings.FAKE_DATE
        min_dist = sys.maxint
        min_dist_round = None

        # prefer later rounds if more than one round take place in parallel
        for tournamentRound in TournamentRound.objects.all().order_by('-display_order'):
            dist = TournamentRound.date_distance_to_round(tournamentRound.pk, test_date)
            if dist < min_dist:
                min_dist = dist
                min_dist_round = tournamentRound
        return min_dist_round

    @staticmethod
    # TODO DEPRECATED, UNTESTED: if required, re-implement in frontend
    def date_distance_to_round(round_id, test_date):
        if Game.objects.filter(round__pk=round_id):
            round_games = Game.objects.filter(round__pk=round_id).order_by('kickoff')
            start = round_games.first().kickoff
            end = round_games.last().kickoff

            if start < test_date < end:
                return 0    # test_date is within round, so 0 seconds away
            else:
                return min(abs(start - test_date).total_seconds(), abs(end - test_date).total_seconds())
        else:
            return timedelta.max.days

    class Meta:
        ordering = ["display_order"]

    def __unicode__(self):  # Python 3: def __str__(self):
        return str(self.name)


class Team(models.Model):
    name = models.CharField(max_length=50, unique=True)
    abbreviation = models.CharField(max_length=3, unique=True)
    group = models.ForeignKey(TournamentGroup)

    class Meta:
        ordering = ["name"]

    def __unicode__(self):  # Python 3: def __str__(self):
        return self.name


class Venue(models.Model):
    name = models.CharField(max_length=50, unique=True)
    city = models.CharField(max_length=50)
    capacity = models.PositiveIntegerField(blank=True, null=True)

    class Meta:
        ordering = ["name"]

    def __unicode__(self):  # Python 3: def __str__(self):
        return self.name + " (" + self.city + ")"


class Game(models.Model):
    kickoff = models.DateTimeField()
    deadline = models.DateTimeField()
    homegoals = models.SmallIntegerField(default=-1)
    awaygoals = models.SmallIntegerField(default=-1)

    hometeam = models.ForeignKey(Team, related_name='games_home')
    awayteam = models.ForeignKey(Team, related_name='games_away')
    venue = models.ForeignKey(Venue)
    round = models.ForeignKey(TournamentRound)

    class Meta:
        ordering = ["kickoff"]

    def result_str(self):
        if hasattr(self, 'homegoals') and self.homegoals != -1 and \
                hasattr(self, 'awaygoals') and self.awaygoals != -1:
            return '%i:%i' % (self.homegoals, self.awaygoals)
        else:
            return '-:-'
    result_str.short_description = 'Result'

    def has_started(self):
        return self.get_reference_date() > self.kickoff

    def deadline_passed(self):
        return self.get_reference_date() > self.deadline

    def is_over(self):
        return self.get_reference_date() > (self.kickoff + timedelta(hours=1, minutes=45))

    def has_result(self):
        return self.homegoals != -1 and self.awaygoals != -1

    @staticmethod
    def get_reference_date():
        return settings.FAKE_DATE if hasattr(settings, 'FAKE_DATE') else timezone.now()

    @staticmethod
    def tournament_has_started():
        games = list(Game.objects.all().order_by('kickoff')[:1])
        if games:
            first_game = games[0]
            reference_date = Game.get_reference_date()
            return reference_date >= first_game.kickoff
        return False

    @staticmethod
    def get_finished_games():
        return Game.objects.exclude(awaygoals=-1).exclude(homegoals=-1)

    @staticmethod
    def get_games_deadline_passed():
        return Game.objects.filter(deadline__lt=timezone.now()).order_by('kickoff')

    @staticmethod
    def get_latest_finished_game():
        games = Game.objects.exclude(homegoals=-1).exclude(awaygoals=-1).order_by('kickoff')
        return games.last() if games else None

    @staticmethod
    def get_first_game():
        first_game = list(Game.objects.filter().order_by('kickoff'))[:1]
        return first_game[0] if first_game else None

    def clean(self):
        if self.deadline is None:
            self.deadline = self.kickoff
        else:
            if self.deadline > self.kickoff:
                raise ValidationError(_('Deadline must not be later than kickoff.'))

        # home/away team consistency
        if hasattr(self, 'hometeam') and self.hometeam is not None and \
                hasattr(self, 'awayteam') and self.awayteam is not None:
            # check if home and awayteam are different
            if self.hometeam == self.awayteam:
                raise ValidationError(_('Home and Away team must be different.'))
            # check if both teams are in same group (if no knock out round)
            if hasattr(self, 'round') and self.round is not None:
                if self.hometeam.group != self.awayteam.group and not self.round.is_knock_out:
                    raise ValidationError(_('This game is not possible. In a non knock-out round both teams '
                                            'must be part of the same group.'))

    def __unicode__(self):  # Python 3: def __str__(self):
        return str(self.hometeam) + ' - ' + str(self.awayteam)


class GameBetResult(models.Model):
    type = models.CharField(max_length=50, unique=True)      # volltreffer, differenz, tendenz, niete ...
    points = models.SmallIntegerField()
    sort_id = models.CharField(max_length=5)

    class Meta:
        ordering = ["sort_id"]

    def __unicode__(self):  # Python 3: def __str__(self):
        return self.type


class GameBet(models.Model):
    homegoals = models.SmallIntegerField(default=-1)
    awaygoals = models.SmallIntegerField(default=-1)
    result_bet_type = models.ForeignKey(GameBetResult, blank=True, null=True, verbose_name='Result Type')

    game = models.ForeignKey(Game)
    user = models.ForeignKey(User)

    class Meta:
        unique_together = ('game', 'user',)

    def bet_str(self):
        if self.homegoals != -1 and self.awaygoals != -1:
            return '%i:%i' % (self.homegoals, self.awaygoals)
        else:
            return '-:-'

    def has_bet(self):
        return self.homegoals != -1 and self.awaygoals != -1

    def has_result(self):
        return self.result_bet_type is not None and self.result_bet_type != ''

    @staticmethod
    def get_user_bets(user_id, finished_only=False):
        if finished_only:
            return GameBet.objects.filter(user__pk=user_id).exclude(result_bet_type__isnull=True)
        else:
            return GameBet.objects.filter(user__pk=user_id)

    @staticmethod
    def get_game_bets(game_id, finished_only=False):
        if finished_only:
            return GameBet.objects.filter(game__pk=game_id).exclude(result_bet_type__isnull=True)
        else:
            return GameBet.objects.filter(game__pk=game_id)

    @staticmethod
    def get_user_game_bet(user_id, game_id):
        game_bets = GameBet.objects.filter(user__pk=user_id).filter(game__pk=game_id)
        return game_bets.first() if game_bets else None

    def compute_gamebet_result_type(self):
        if not self.game or not self.game.has_result() or not self.has_bet():
            self.result_bet_type = None
            self.save()
            return

        # TODO hardcoded... but flexible ResultTypes do not really make sense unless they store their own comparison logic...
        volltreffer = GameBetResult.objects.get(type__iexact='volltreffer')
        differenz = GameBetResult.objects.get(type__iexact='differenz')
        remis_tendenz = GameBetResult.objects.get(type__iexact='remis-tendenz')
        tendenz = GameBetResult.objects.get(type__iexact='tendenz')
        niete = GameBetResult.objects.get(type__iexact='niete')

        (game_hg, game_ag) = (int(self.game.homegoals), int(self.game.awaygoals))
        (bet_hg, bet_ag) = (int(self.homegoals), int(self.awaygoals))

        if game_hg == bet_hg and game_ag == bet_ag:
            self.result_bet_type = volltreffer
            self.save()
            return

        if (game_hg - game_ag) == (bet_hg - bet_ag):
            if game_hg == game_ag:
                # game was a remis
                self.result_bet_type = remis_tendenz
                self.save()
                return
            else:
                # game was no remis
                self.result_bet_type = differenz
                self.save()
                return

        if (game_hg - game_ag) * (bet_hg - bet_ag) > 0:
            self.result_bet_type = tendenz
            self.save()
            return

        if game_hg is game_ag and bet_hg is bet_ag:
            self.result_bet_type = tendenz
            self.save()
            return

        self.result_bet_type = niete
        self.save()

    def __unicode__(self):  # Python 3: def __str__(self):
        return self.bet_str()


class Extra(models.Model):
    """
        "Zusatztipps".
    """

    name = models.CharField(max_length=50, unique=True)
    points = models.SmallIntegerField(default=10)
    deadline = models.DateTimeField()
    result = models.CharField(blank=True, max_length=50)

    def has_result(self):
        return self.result is not None and self.result != ''

    def deadline_passed(self):
        return self.get_reference_date() > self.deadline

    @staticmethod
    def get_finished_extras():
        return Extra.objects.exclude(result__isnull=True).exclude(result__exact='')

    def get_reference_date(self):
        return settings.FAKE_DATE if hasattr(settings, 'FAKE_DATE') else timezone.now()

    def __unicode__(self):  # Python 3: def __str__(self):
        return self.name


class ExtraChoice(models.Model):
    name = models.CharField(max_length=50)
    extra = models.ForeignKey(Extra, related_name='choices')
    sort_index = models.CharField(blank=True, max_length=10)

    class Meta:
        ordering = ['sort_index', 'name']
        unique_together = ('name', 'extra',)

    def __unicode__(self):  # Python 3: def __str__(self):
        return self.name


class ExtraBet(models.Model):
    result_bet = models.CharField(blank=True, max_length=50)

    extra = models.ForeignKey(Extra)
    user = models.ForeignKey(User)

    class Meta:
        unique_together = ('extra', 'user',)

    def bet_str(self):
        if hasattr(self, 'result_bet') and self.result_bet:
            return self.result_bet
        else:
            return '---'

    @staticmethod
    def get_user_bets(user_id):
        return ExtraBet.objects.filter(user__pk=user_id)

    @staticmethod
    def get_extra_bets(extra_id):
        return ExtraBet.objects.filter(extra__pk=extra_id)

    @staticmethod
    def get_user_extra_bet(user_id, extra_id):
        extra_bets = ExtraBet.objects.filter(user__pk=user_id).filter(extra__pk=extra_id)
        return extra_bets.first() if extra_bets else None

    def compute_points(self):
        if self.result_bet == self.extra.result:
            return self.extra.points
        else:
            return 0

    def __unicode__(self):  # Python 3: def __str__(self):
        return self.result_bet


class Statistic(models.Model):
    user = models.OneToOneField(User, primary_key=True)

    no_bets = models.PositiveSmallIntegerField(default=0)

    no_volltreffer = models.PositiveSmallIntegerField(default=0)
    no_differenz = models.PositiveSmallIntegerField(default=0)
    no_remis_tendenz = models.PositiveSmallIntegerField(default=0)
    no_tendenz = models.PositiveSmallIntegerField(default=0)
    no_niete = models.PositiveSmallIntegerField(default=0)

    points = models.PositiveSmallIntegerField(default=0)

    def recalculate(self):
        """
            Re-calculate statistics based on all bets for this user
        """
        self.points, self.no_volltreffer, self.no_differenz, self.no_remis_tendenz, \
            self.no_tendenz, self.no_niete = 0, 0, 0, 0, 0, 0

        if Game.tournament_has_started():
            for game_bet in GameBet.get_user_bets(self.user.pk, True):
                if game_bet.game.has_result():
                    self.points += game_bet.result_bet_type.points
                    result_bet_type = game_bet.result_bet_type.type.lower()
                    if result_bet_type == 'volltreffer':
                        self.no_volltreffer += 1
                    elif result_bet_type == 'differenz':
                        self.no_differenz += 1
                    elif result_bet_type == 'remis-tendenz':
                        self.no_remis_tendenz += 1
                    elif result_bet_type == 'tendenz':
                        self.no_tendenz += 1
                    elif result_bet_type == 'niete':
                        self.no_niete += 1

            for extra_bet in ExtraBet.get_user_bets(self.user.pk):
                if extra_bet.extra.has_result():
                    pts = extra_bet.compute_points()
                    self.points += pts
                    if pts > 0:
                        self.no_volltreffer += 1
                    else:
                        self.no_niete += 1

    def update_no_bets(self):
        """
            Count number of bets this user has placed
        """
        self.no_bets = 0

        if Game.tournament_has_started():
            for game_bet in GameBet.get_user_bets(self.user.pk):
                if game_bet.has_bet():
                    self.no_bets += 1
            for extra_bet in ExtraBet.get_user_bets(self.user.pk):
                if extra_bet.result_bet:
                    self.no_bets += 1

    def pretty_print(self):
        return "%s (%i bets, %i Volltreffer, %i Points)" % (self.user, self.no_bets, self.no_volltreffer, self.points)

    def __unicode__(self):
        return "%s's statistics" % self.user


###########
# SIGNAL OVERRIDES
###########

# automatically create a profile and a statistic for each new user
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
        Statistic.objects.create(user=instance)


@receiver(post_save, sender=Game)
def update_game_bet_results(sender, instance, created, **kwargs):
    game_id_to_update = instance.pk
    for gamebet in GameBet.get_game_bets(game_id_to_update):
        gamebet.compute_gamebet_result_type()


# update no_bets on user statistic
@receiver(post_save, sender=GameBet)
@receiver(post_save, sender=ExtraBet)
def update_statistic_no_bets(sender, instance, created, **kwargs):
    instance.user.statistic.update_no_bets()
    instance.user.statistic.save()


@receiver(post_save, sender=Extra)
@receiver(post_save, sender=Game)
def update_user_statistics(sender, instance, created, **kwargs):
    for user in User.objects.all():
        user.statistic.recalculate()
        user.statistic.update_no_bets()
        user.statistic.save()


class Profile(models.Model):
    user = models.OneToOneField(User, primary_key=True)
    email2 = models.EmailField(blank=True)

    avatar = models.ImageField(upload_to=utils.get_avatar_path, storage=OverwriteStorage(), blank=True, null=True)
    avatar_cropped = models.ImageField(upload_to=utils.get_thumb_path, storage=OverwriteStorage(), blank=True, null=True)

    about = models.CharField(max_length=500, blank=True, null=True)
    location = models.CharField(max_length=50, blank=True)

    has_paid = models.BooleanField(default=False)

    reminder_emails = models.BooleanField(blank=False, default=True)
    daily_emails = models.BooleanField(blank=False, default=True)

    class Meta:
        ordering = ['user']

    def get_display_name(self):
        full_name = self.user.get_full_name()
        return full_name if full_name else self.user.username

    def avatar_tag(self):
        if self.avatar:
            return '<img src="%s" />' % self.avatar.url
        else:
            return 'No avatar.'

    # TODO add to model tests!
    def get_open_bets(self):
        open_bets = []
        open_games = Game.objects.all()
        for game in open_games:
            gamebet = GameBet.get_user_game_bet(self.user.pk, game.pk)
            if not game.deadline_passed():
                if gamebet and not gamebet.has_bet():
                    open_bets.append(game)
                elif not gamebet:
                    open_bets.append(game)
        return open_bets

    # TODO add to model tests!
    def get_open_extras(self):
        open_bets = []
        open_extras = Extra.objects.all()
        for extra in open_extras:
            extrabet = ExtraBet.get_user_extra_bet(self.user.pk, extra.pk)
            if not extrabet and not extra.deadline_passed():
                open_bets.append(extra)
        return open_bets

    def __unicode__(self):  # Python 3: def __str__(self):
        return str(self.user) + '\'s Profile'


class Post(models.Model):
    title = models.TextField()
    content = models.TextField()
    author = models.ForeignKey(User, related_name='authored_posts')

    date_created = models.DateTimeField(auto_now_add=True)
    finished = models.BooleanField(default=True)

    news_appear = models.BooleanField(default=True)
    as_mail = models.BooleanField(default=False)
    force_mail = models.BooleanField(default=False)

    def clean(self):
        # blank posts are not allowed. This has to be validated here, cannot be validate by the TextField itself
        # (blank=False only applies to Django forms)
        if not self.title:
            raise ValidationError(_('Title must not be empty.'))
        if not self.content:
            raise ValidationError(_('Content must not be empty.'))

    def __unicode__(self):  # Python 3: def __str__(self):
        return u"Post by " + str(self.author)


@receiver(post_save, sender=Post)
def send_post_as_mail(sender, instance, created, **kwargs):
    if instance.as_mail:
        utils.send_mail_to_users(instance, instance.force_mail)
