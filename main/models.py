# -*- coding: utf-8 -*-
from datetime import *

from django.contrib.auth.models import User
from django.db import models, utils
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import ugettext as _

from main import utils
from main.storage import OverwriteStorage
from main.validators import *


class TournamentGroup(models.Model):
    name = models.CharField(max_length=20, unique=True)
    abbreviation = models.CharField(max_length=3, unique=True)

    class Meta:
        app_label = 'main'
        ordering = ["name"]

    def __str__(self):
        return self.name


class TournamentRound(models.Model):
    name = models.CharField(max_length=50, unique=True)
    is_knock_out = models.BooleanField(default=False, blank=False)
    display_order = models.PositiveSmallIntegerField()
    abbreviation = models.CharField(max_length=3, blank=True)

    def get_all_games(self):
        return Game.objects.filter(round=self)

    class Meta:
        ordering = ["display_order"]

    def __str__(self):
        return str(self.name)


class Team(models.Model):
    name = models.CharField(max_length=50, unique=True)
    abbreviation = models.CharField(max_length=3, unique=True)
    group = models.ForeignKey(TournamentGroup)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Venue(models.Model):
    name = models.CharField(max_length=50, unique=True)
    city = models.CharField(max_length=50)
    capacity = models.PositiveIntegerField(blank=True, null=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name + " (" + self.city + ")"


class ResultBetType(utils.ChoicesEnum):
    volltreffer = 'Volltreffer'
    differenz = 'Differenz'
    remis_tendenz = 'Remis Tendenz'
    tendenz = 'Tendenz'
    niete = 'Niete'


class Bettable(models.Model):
    deadline = models.DateTimeField()
    name = models.CharField(max_length=50, unique=True)
    result = models.CharField(blank=True, null=True, max_length=50)

    class Meta:
        ordering = ["deadline", "name"]

    def deadline_passed(self):
        return utils.get_reference_date() > self.deadline

    def has_result(self):
        return self.result is not None and self.result != ''

    def get_related_child(self):
        if hasattr(self, 'game'):
            return self.game
        elif hasattr(self, 'extra'):
            return self.extra
        return None

    @staticmethod
    def get_bettables_with_result():
        return Bettable.objects.exclude(result__isnull=True).exclude(result__exact='')

    def __str__(self):
        return str(self.name)


class Game(Bettable):
    kickoff = models.DateTimeField()
    homegoals = models.SmallIntegerField(default=-1)
    awaygoals = models.SmallIntegerField(default=-1)

    hometeam = models.ForeignKey(Team, related_name='games_home')
    awayteam = models.ForeignKey(Team, related_name='games_away')
    venue = models.ForeignKey(Venue)
    round = models.ForeignKey(TournamentRound)

    class Meta:
        ordering = ["kickoff"]

    def result_str(self):
        if self.has_result():
            return '%i:%i' % (self.homegoals, self.awaygoals)
        else:
            return '-:-'
    result_str.short_description = 'Result'

    def has_result(self):
        return hasattr(self, 'homegoals') and self.homegoals != -1 and \
                hasattr(self, 'awaygoals') and self.awaygoals != -1

    def has_started(self):
        return utils.get_reference_date() > self.kickoff

    def is_over(self):
        return utils.get_reference_date() > (self.kickoff + timedelta(hours=1, minutes=45))

    @staticmethod
    def tournament_has_started():
        games = list(Game.objects.all().order_by('kickoff')[:1])
        if games:
            first_game = games[0]
            reference_date = utils.get_reference_date()
            return reference_date >= first_game.kickoff
        return False

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

    def __str__(self):
        return str(self.hometeam) + ' - ' + str(self.awayteam)


class Extra(Bettable):
    """ Zusatztipps """
    points = models.SmallIntegerField(default=10)


# TODO could maybe generalised to a BettableChoice? (although YAGNI?)
class ExtraChoice(models.Model):
    name = models.CharField(max_length=50)
    extra = models.ForeignKey(Extra, related_name='choices')
    sort_index = models.CharField(blank=True, max_length=10)

    class Meta:
        ordering = ['sort_index', 'name']
        unique_together = ('name', 'extra',)

    def __str__(self):
        return self.name


class Bet(models.Model):
    result_bet = models.CharField(blank=True, max_length=50)
    result_bet_type = models.CharField(blank=True, null=True,
                                       choices=ResultBetType.choices(), max_length=50)
    points = models.PositiveSmallIntegerField(blank=True, null=True)

    bettable = models.ForeignKey(Bettable)
    user = models.ForeignKey(User)

    class Meta:
        unique_together = ('bettable', 'user',)

    def bet_str(self):
        if hasattr(self, 'result_bet') and self.has_bet():
            return self.result_bet
        else:
            return '---'

    def has_bet(self):
        return self.result_bet is not None and self.result_bet != ''

    def get_gamebet_goals(self):
        if self.has_bet():
            return [int(it) for it in self.result_bet.split(":")]
        else:
            return -1, -1

    # TODO DRY up
    @staticmethod
    def get_user_bets(user_id, bettable_has_result = False):
        bets_set = Bet.objects.filter(user__pk=user_id)
        if bettable_has_result:
            return filter(lambda bet: bet.bettable.has_result(),
                          list(bets_set
                               .exclude(result_bet__isnull=True)
                               .exclude(result_bet__exact='')
                               .order_by('bettable__deadline', 'bettable__name')))
        else:
            return bets_set.order_by('bettable__deadline', 'bettable__name')

    @staticmethod
    def get_bets_for_bettable(bettable_id, bettable_has_result = False):
        bets_set = Bet.objects.filter(bettable__pk=bettable_id)
        if bettable_has_result:
            return filter(lambda bet: bet.bettable.has_result(),
                          list(bets_set
                               .exclude(result_bet__isnull=True)
                               .exclude(result_bet__exact='')
                               .order_by('bettable__deadline', 'bettable__name')))
        else:
            return bets_set.order_by('bettable__deadline', 'bettable__name')

    @staticmethod
    def get_user_bettable_bet(user_id, bettable_id):
        bettables = Bet.objects.filter(user__pk=user_id).filter(bettable__pk=bettable_id)
        return bettables.first() if bettables else None

    def compute_points(self):
        if not self.bettable or not self.bettable.has_result() or not self.has_bet():
            self.result_bet_type = None
            self.save()
            return

        if hasattr(self.bettable, 'extra'):
            if self.result_bet == self.bettable.result:
                self.result_bet_type = ResultBetType.volltreffer
                self.points = self.bettable.extra.points
            else:
                self.result_bet_type = ResultBetType.niete
                self.points = 0
            self.save()
        elif hasattr(self.bettable, 'game'):
            self.compute_points_of_game_bettable()

    def compute_points_of_game_bettable(self):
        if not self.has_bet() or not self.bettable.has_result():
            return

        bettable_game = self.bettable.game

        # TODO hardcoded points... move to settings? or think about how to dynamically expose them via the API
        volltreffer = (ResultBetType.volltreffer, 5)
        differenz = (ResultBetType.differenz, 3)
        remis_tendenz = (ResultBetType.remis_tendenz, 2)
        tendenz = (ResultBetType.tendenz, 1)
        niete = (ResultBetType.niete, 0)

        (game_hg, game_ag) = (int(bettable_game.homegoals), int(bettable_game.awaygoals))
        (bet_hg, bet_ag) = self.get_gamebet_goals()

        if game_hg == bet_hg and game_ag == bet_ag:
            self.result_bet_type = volltreffer[0].name
            self.points = volltreffer[1]
            self.save()
            return

        if (game_hg - game_ag) == (bet_hg - bet_ag):
            if game_hg == game_ag:
                # game was a remis
                self.result_bet_type = remis_tendenz[0].name
                self.points = remis_tendenz[1]
                self.save()
                return
            else:
                # game was no remis
                self.result_bet_type = differenz[0].name
                self.points = differenz[1]
                self.save()
                return

        if (game_hg - game_ag) * (bet_hg - bet_ag) > 0:
            self.result_bet_type = tendenz[0].name
            self.points = tendenz[1]
            self.save()
            return

        if game_hg is game_ag and bet_hg is bet_ag:
            self.result_bet_type = tendenz[0].name
            self.points = tendenz[1]
            self.save()
            return

        self.result_bet_type = niete[0].name
        self.points = niete[1]
        self.save()

    def __str__(self):
        return self.bet_str()


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
            for bet in Bet.get_user_bets(self.user.pk, True):
                self.points += bet.points
                result_bet_type = bet.result_bet_type
                if result_bet_type == ResultBetType.volltreffer:
                    self.no_volltreffer += 1
                elif result_bet_type == ResultBetType.differenz:
                    self.no_differenz += 1
                elif result_bet_type == ResultBetType.remis_tendenz:
                    self.no_remis_tendenz += 1
                elif result_bet_type == ResultBetType.tendenz:
                    self.no_tendenz += 1
                elif result_bet_type == ResultBetType.niete:
                    self.no_niete += 1


    def update_no_bets(self):
        """
            Count number of bets this user has placed
        """
        self.no_bets = 0
        # TODO this can probably be simplified? Result set filter, count?
        if Game.tournament_has_started():
            for bet in Bet.get_user_bets(self.user.pk):
                if bet.has_bet():
                    self.no_bets += 1

    def pretty_print(self):
        return "%s (%i bets, %i Volltreffer, %i Points)" % (self.user, self.no_bets, self.no_volltreffer, self.points)

    def __str__(self):
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
@receiver(post_save, sender=Extra)
def update_bet_results(sender, instance, created, **kwargs):
    if isinstance(instance, Game) and instance.has_result() and hasattr(instance, 'bettable_ptr'):
        instance.bettable_ptr.result = instance.result_str()
        instance.bettable_ptr.save()

    print("COMPUTE POINTS")
    for bet in Bet.get_bets_for_bettable(instance.pk):
        bet.compute_points()

    # print("RECALCULATE STATS")
    # for user in User.objects.all():
    #     user.statistic.recalculate()
    #     user.statistic.update_no_bets()
    #     user.statistic.save()


# update no_bets on user statistic
@receiver(post_save, sender=Bet)
def update_statistic_no_bets(sender, instance, created, **kwargs):
    print("POST_SAVE BET, update bet count stats")
    instance.user.statistic.update_no_bets()
    instance.user.statistic.save()


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
    def get_open_bettables(self):
        open_bettables = []
        for bettable in Bettable.objects.all():
            bet = Bet.get_user_bettable_bet(self.user.pk, bettable.pk)
            if not bettable.deadline_passed():
                if not bet or (bet and not bet.has_bet()):
                    open_bettables.append(bettable)
        return open_bettables

    def __str__(self):
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

    def __str__(self):
        return u"Post by " + str(self.author)


@receiver(post_save, sender=Post)
def send_post_as_mail(sender, instance, created, **kwargs):
    if instance.as_mail:
        utils.send_mail_to_users(instance, instance.force_mail)
