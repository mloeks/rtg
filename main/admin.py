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
        ('Game details', {'fields': ['round', 'kickoff', 'deadline', 'venue', 'hometeam', 'awayteam', 'homegoals', 'awaygoals']}),
    ]
    list_display = ('__str__', 'round', 'kickoff', 'deadline', 'result_str', 'venue')
    list_filter = ['round', 'kickoff', 'deadline', 'venue']


class GameBetResultAdmin(admin.ModelAdmin):
    list_display = ('type', 'points')


class GameBetAdmin(admin.ModelAdmin):
    fields = ('user', 'game', 'homegoals', 'awaygoals')
    list_display = ('__str__', 'user', 'game')
    list_filter = ['user', 'game']


class ExtraChoiceInline(admin.TabularInline):
    model = ExtraChoice
    extra = 10


class ExtraAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'points')
    inlines = [ExtraChoiceInline]


class ExtraChoiceAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'extra')
    list_filter = ['extra']


class ExtraBetAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'user', 'extra')
    list_filter = ['result_bet', 'extra']


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
    list_display = ('__str__', 'date_created')

###########################

admin.site.register(TournamentGroup, TournamentGroupAdmin)
admin.site.register(TournamentRound, TournamentRoundAdmin)
admin.site.register(Team, TeamAdmin)
admin.site.register(Venue, VenueAdmin)
admin.site.register(Game, GameAdmin)

admin.site.register(GameBetResult, GameBetResultAdmin)
admin.site.register(GameBet, GameBetAdmin)
admin.site.register(Extra, ExtraAdmin)
admin.site.register(ExtraChoice, ExtraChoiceAdmin)
admin.site.register(ExtraBet, ExtraBetAdmin)

admin.site.register(Profile, ProfileAdmin)
admin.site.register(Statistic, StatisticAdmin)
admin.site.register(Post, PostAdmin)