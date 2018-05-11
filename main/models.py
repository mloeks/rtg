# -*- coding: utf-8 -*-
from datetime import *

from django.contrib.auth.models import User
from django.db import models, utils
from django.db.models import Q
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
    name = models.CharField(max_length=50)
    result = models.CharField(blank=True, null=True, max_length=50)

    class Meta:
        ordering = ["deadline", "name"]

    def deadline_passed(self):
        return utils.get_reference_date() >= self.deadline

    def has_result(self):
        return self.result is not None and self.result != ''

    def set_result(self, result):
        self.result = result
        self.save()

    def remove_result(self):
        self.result = None
        self.save()

    def get_related_child(self):
        if hasattr(self, 'game'):
            return self.game
        elif hasattr(self, 'extra'):
            return self.extra
        return None

    @staticmethod
    def get_open_bettables_for_user(user_id):
        return Bettable.objects\
            .filter(deadline__gte=utils.get_reference_date())\
            .exclude(Q(bet__user=user_id) & Q(bet__result_bet__isnull=False) & ~Q(bet__result_bet__exact=''))

    @staticmethod
    def get_bettables_with_result():
        return Bettable.objects.exclude(result__isnull=True).exclude(result__exact='')

    def __str__(self):
        return str(self.name)


# TODO P2 connect with OpenLigaDb Web Service, update results automatically
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
        unique_together = ('hometeam', 'awayteam', 'round')

    def result_str(self):
        return '%i:%i' % (self.homegoals, self.awaygoals) if self.has_result() else None

    result_str.short_description = 'Result'

    def has_result(self):
        return hasattr(self, 'homegoals') and self.homegoals != -1 and \
                hasattr(self, 'awaygoals') and self.awaygoals != -1

    def has_started(self):
        return utils.get_reference_date() > self.kickoff

    def is_over(self):
        return utils.get_reference_date() > (self.kickoff + timedelta(hours=1, minutes=45))

    def set_result_goals(self, homegoals, awaygoals):
        self.homegoals = homegoals
        self.awaygoals = awaygoals
        super().set_result(self.result_str())
        self.save()

    def remove_result(self):
        self.homegoals = -1
        self.awaygoals = -1
        super().remove_result()
        self.save()

    def update_bettable_name(self):
        self.bettable_ptr.name = "%s - %s" % (self.hometeam, self.awayteam,)
        self.bettable_ptr.save()

    def update_bettable_result_field(self):
        self.bettable_ptr.result = self.result_str()
        self.bettable_ptr.save()

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


# TODO P3 could maybe generalised to a BettableChoice? (although YAGNI?)
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

    @staticmethod
    def get_by_user(user_id):
        return Bet.objects \
            .filter(user__pk=user_id) \
            .order_by('bettable__deadline', 'bettable__name')

    @staticmethod
    def get_by_user_and_bettable_has_result(user_id):
        return Bet.get_by_user(user_id) \
            .exclude(bettable__result__isnull=True) \
            .exclude(bettable__result__exact='')

    @staticmethod
    def get_by_user_and_has_bet(user_id):
        return Bet.get_by_user(user_id) \
            .exclude(result_bet__isnull=True) \
            .exclude(result_bet__exact='')

    @staticmethod
    def get_by_user_and_has_bet_and_bettable_has_result(user_id):
        return Bet.get_by_user_and_has_bet(user_id) \
            .exclude(bettable__result__isnull=True) \
            .exclude(bettable__result__exact='')

    @staticmethod
    def get_by_bettable(bettable_id):
        return Bet.objects\
            .filter(bettable__pk=bettable_id)\
            .order_by('bettable__deadline', 'bettable__name')

    @staticmethod
    def get_by_bettable_and_has_result_and_bettable_has_result(bettable_id):
        return Bet.get_by_bettable(bettable_id)\
            .exclude(result_bet__isnull=True)\
            .exclude(result_bet__exact='')\
            .exclude(bettable__result__isnull=True)\
            .exclude(bettable__result__exact='')

    @staticmethod
    def get_by_user_and_bettable(user_id, bettable_id):
        bettables = Bet.objects.filter(user__pk=user_id).filter(bettable__pk=bettable_id)
        return bettables.first() if bettables else None

    def compute_points(self):
        if not self.bettable or not self.bettable.has_result() or not self.has_bet():
            self.points = None
            self.result_bet_type = None
            self.save()
            return

        if hasattr(self.bettable, 'extra'):
            self.compute_points_of_extra_bettable()
        elif hasattr(self.bettable, 'game'):
            self.compute_points_of_game_bettable()

        self.save()

    def compute_points_of_extra_bettable(self):
        if self.result_bet == self.bettable.result:
            self.result_bet_type = ResultBetType.volltreffer.name
            self.points = self.bettable.extra.points
        else:
            self.result_bet_type = ResultBetType.niete.name
            self.points = 0

    def compute_points_of_game_bettable(self):
        if not self.has_bet() or not self.bettable.has_result():
            return

        bettable_game = self.bettable.game

        # TODO P3 hardcoded points... move to settings? or think about how to dynamically expose them via the API
        volltreffer = (ResultBetType.volltreffer.name, 5)
        differenz = (ResultBetType.differenz.name, 3)
        remis_tendenz = (ResultBetType.remis_tendenz.name, 2)
        tendenz = (ResultBetType.tendenz.name, 1)
        niete = (ResultBetType.niete.name, 0)

        (game_hg, game_ag) = (int(bettable_game.homegoals), int(bettable_game.awaygoals))
        (bet_hg, bet_ag) = self.get_gamebet_goals()

        if game_hg == bet_hg and game_ag == bet_ag:
            self.result_bet_type, self.points = volltreffer
            return

        if (game_hg - game_ag) == (bet_hg - bet_ag):
            if game_hg == game_ag:
                # game was a remis
                self.result_bet_type, self.points = remis_tendenz
                return
            else:
                # game was no remis
                self.result_bet_type, self.points = differenz
                return

        if (game_hg - game_ag) * (bet_hg - bet_ag) > 0:
            self.result_bet_type, self.points = tendenz
            return

        if game_hg is game_ag and bet_hg is bet_ag:
            self.result_bet_type, self.points = tendenz
            return

        self.result_bet_type, self.points = niete

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

    def update(self):
        self.recalculate()
        self.update_no_bets()
        self.save()

    def recalculate(self):
        """
            Re-calculate statistics based on all bets for this user
        """
        self.points, self.no_volltreffer, self.no_differenz, self.no_remis_tendenz, \
            self.no_tendenz, self.no_niete = 0, 0, 0, 0, 0, 0

        for bet in Bet.get_by_user_and_has_bet_and_bettable_has_result(self.user.pk):
            if bet.points is not None:
                self.points += bet.points
                result_bet_type = bet.result_bet_type
                if result_bet_type == ResultBetType.volltreffer.name:
                    self.no_volltreffer += 1
                elif result_bet_type == ResultBetType.differenz.name:
                    self.no_differenz += 1
                elif result_bet_type == ResultBetType.remis_tendenz.name:
                    self.no_remis_tendenz += 1
                elif result_bet_type == ResultBetType.tendenz.name:
                    self.no_tendenz += 1
                elif result_bet_type == ResultBetType.niete.name:
                    self.no_niete += 1

    def update_no_bets(self):
        """
            Count number of bets this user has placed
        """
        self.no_bets = Bet.get_by_user_and_has_bet(self.user.pk).count()

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
    # update result field on Game bettables, which are stored by setting the goals, but not the result string
    if isinstance(instance, Game) and hasattr(instance, 'bettable_ptr'):
        instance.update_bettable_name()
        instance.update_bettable_result_field()

    [bet.compute_points() for bet in Bet.get_by_bettable(instance.pk)]
    [user.statistic.update() for user in User.objects.all()]


# update no_bets on user statistic
@receiver(post_save, sender=Bet)
def update_statistic_no_bets(sender, instance, created, **kwargs):
    instance.user.statistic.update_no_bets()
    instance.user.statistic.save()


class Profile(models.Model):
    user = models.OneToOneField(User, primary_key=True)
    email2 = models.EmailField(blank=True, default='')

    avatar = models.ImageField(upload_to=utils.get_avatar_path, storage=OverwriteStorage(), blank=True, null=True)

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

    def get_open_bettables(self):
        return Bettable.get_open_bettables_for_user(self.user.pk)

    def get_open_bettables_deadline_within(self, delta):
        reference_date_plus_delta = utils.get_reference_date() + delta
        return self.get_open_bettables().filter(deadline__lte=reference_date_plus_delta)

    def avatar_tag(self):
        if self.avatar:
            return '<img src="%s" />' % self.avatar.url
        else:
            return 'No avatar.'

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


# TODO P3 introduce likes on comments
class Comment(models.Model):
    content = models.TextField()
    author = models.ForeignKey(User, related_name='comments')
    post = models.ForeignKey(Post, related_name='comments')
    reply_to = models.ForeignKey("self", related_name='replies')

    date_created = models.DateTimeField(auto_now_add=True)
    removed = models.BooleanField(default=False)

    def clean(self):
        # blank comments are not allowed. This has to be validated here, cannot be validate by the TextField itself
        # (blank=False only applies to Django forms)
        if not self.content:
            raise ValidationError(_('Content must not be empty.'))

    def __str__(self):
        return u"Comment by " + str(self.author)


@receiver(post_save, sender=Post)
def send_post_as_mail(sender, instance, created, **kwargs):
    if instance.as_mail or instance.force_mail:
        utils.send_mail_to_users(instance, instance.force_mail)
