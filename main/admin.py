from django.contrib import admin

from main.models import *


class TournamentGroupAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'abbreviation')


class TournamentRoundAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'is_knock_out')


class TeamAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'group')
    list_filter = ['group']
    search_fields = ['name', 'abbreviation']


class VenueAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'capacity')
    search_fields = ['name', 'city']


class GameAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Game details',
         {'fields': ['round', 'kickoff', 'deadline', 'venue', 'hometeam', 'awayteam',
                     'homegoals', 'awaygoals', 'openligadb_match_id']}),
    ]
    list_display = ('pk', 'openligadb_match_id', '__str__', 'round', 'kickoff', 'deadline', 'result_str', 'venue')
    list_filter = ['round', 'kickoff', 'deadline', 'venue']


class BetAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'user', 'bettable')
    list_filter = ['user', 'result_bet', 'bettable']


class BettableAdmin(admin.ModelAdmin):
    list_display = ('name', 'deadline', 'result')
    list_filter = ['name', 'deadline', 'result']


class ExtraChoiceInline(admin.TabularInline):
    model = ExtraChoice
    extra = 10


class ExtraAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'points', 'deadline')
    inlines = [ExtraChoiceInline]


class ExtraChoiceAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'extra')
    list_filter = ['extra']


class ProfileAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'avatar_tag', 'has_paid')
    fields = ['user', 'has_paid']


class StatisticAdmin(admin.ModelAdmin):

    user = models.OneToOneField(User, primary_key=True)

    no_bets = models.PositiveSmallIntegerField(default=0)
    no_volltreffer = models.PositiveSmallIntegerField(default=0)
    points = models.PositiveSmallIntegerField(default=0)

    list_display = ('user', 'no_bets', 'no_volltreffer', 'points')


class PostAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'date_created', 'title', 'news_appear', 'as_mail')


class CommentAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'date_created', 'content')

###########################

admin.site.register(TournamentGroup, TournamentGroupAdmin)
admin.site.register(TournamentRound, TournamentRoundAdmin)
admin.site.register(Team, TeamAdmin)
admin.site.register(Venue, VenueAdmin)
admin.site.register(Game, GameAdmin)

admin.site.register(Extra, ExtraAdmin)
admin.site.register(ExtraChoice, ExtraChoiceAdmin)

admin.site.register(Bet, BetAdmin)
admin.site.register(Bettable, BettableAdmin)

admin.site.register(Profile, ProfileAdmin)
admin.site.register(Statistic, StatisticAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(Comment, CommentAdmin)