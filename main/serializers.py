# -*- coding: utf-8 -*-
from django.template.defaultfilters import lower
from rest_framework import serializers
from rest_framework.fields import CharField, ImageField

from main import registration_overrides
from main.models import *


class BetSerializer(serializers.ModelSerializer):
    # needs to be specified explicitly with default because it is part of a unique_together relation in the model
    user = serializers.PrimaryKeyRelatedField(read_only=True, default=serializers.CurrentUserDefault())

    bettable_type = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Bet
        fields = '__all__'
        read_only_fields = ('points', 'result_bet_type',)

    def get_bettable_type(self, obj):
        return lower(type(obj.bettable.get_related_child()).__name__)

    def validate(self, attrs):
        if attrs['bettable'].deadline_passed():
            raise serializers.ValidationError({ 'detail': 'Die Deadline ist abgelaufen.', 'code': 'DEADLINE_PASSED'})
        return attrs


class BettableSerializer(serializers.ModelSerializer):
    type = serializers.SerializerMethodField()

    class Meta:
        model = Bettable
        fields = ('id', 'deadline', 'name', 'result', 'type')

    def get_type(self, obj):
        return lower(type(obj.get_related_child()).__name__)


class ExtraChoiceNameField(serializers.RelatedField):
    def to_representation(self, value):
        return value.name


class ExtraSerializer(serializers.ModelSerializer):
    choices = ExtraChoiceNameField(many=True, read_only=True)
    open = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Extra
        fields = ('id', 'name', 'points', 'deadline', 'result', 'choices', 'open')

    def get_open(self, obj):
        return not obj.deadline_passed()


class TournamentGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = TournamentGroup
        fields = ('id', 'name', 'abbreviation')

    @staticmethod
    def as_dict(obj):
        return {
            'id': obj.pk,
            'name': obj.name,
            'abbreviation': obj.abbreviation
        }


class TournamentRoundSerializer(serializers.ModelSerializer):
    class Meta:
        model = TournamentRound
        fields = '__all__'

    @staticmethod
    def as_dict(obj):
        return {
            'name': obj.name,
            'abbreviation': obj.abbreviation,
            'is_knock_out': obj.is_knock_out
        }


class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = '__all__'

    def to_representation(self, instance):
        return {
            'id': instance.pk,
            'name': instance.name,
            'abbreviation': instance.abbreviation,
            'group': TournamentGroupSerializer.as_dict(instance.group),
        }


class VenueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Venue
        fields = '__all__'


# TODO P3 validate various possible inconsistencies (cf. model, is not applied here at all!)
class GameSerializer(serializers.ModelSerializer):
    city = serializers.SerializerMethodField()
    bets_open = serializers.SerializerMethodField()
    round_details = serializers.SerializerMethodField()
    group = serializers.SerializerMethodField(allow_null=True)

    hometeam_name = serializers.CharField(source='hometeam.name', read_only=True)
    awayteam_name = serializers.CharField(source='awayteam.name', read_only=True)

    hometeam_abbreviation = serializers.CharField(source='hometeam.abbreviation', read_only=True)
    awayteam_abbreviation = serializers.CharField(source='awayteam.abbreviation', read_only=True)

    class Meta:
        model = Game
        fields = ('id', 'kickoff', 'deadline', 'hometeam', 'hometeam_name', 'hometeam_abbreviation',
                  'awayteam', 'awayteam_name', 'awayteam_abbreviation', 'homegoals', 'awaygoals',
                  'city', 'round', 'group', 'round_details', 'venue', 'bets_open')
        extra_kwargs = {
            'hometeam': {'write_only': True},
            'awayteam': {'write_only': True},
            'round': {'write_only': True},
            'venue': {'write_only': True},
        }

    def get_bets_open(self, obj):
        return not obj.deadline_passed()

    def get_city(self, obj):
        return obj.venue.city

    def get_round_details(self, obj):
        return TournamentRoundSerializer.as_dict(obj.round)

    def get_group(self, obj):
        return TournamentGroupSerializer.as_dict(obj.hometeam.group) if not obj.round.is_knock_out else None


class GameKickoffsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = ('kickoff',)

    def to_representation(self, instance):
        return str(instance.kickoff)

# Combining custom Profile with User, cf. https://stackoverflow.com/a/28733782
class UserSerializer(serializers.ModelSerializer):
    # TODO P3 where does the min_length 3 requirement actually come from?
    username = serializers.CharField(validators=registration_overrides.rtg_username_validators,
                                     min_length=3, max_length=150)
    email = serializers.EmailField(allow_blank=False)
    email2 = serializers.EmailField(source='profile.email2', required=False, allow_blank=True)
    avatar = ImageField(source='profile.avatar', required=False, allow_null=True, read_only=True)
    about = serializers.CharField(source='profile.about', required=False, allow_blank=True)
    location = serializers.CharField(source='profile.location', required=False, allow_blank=True)
    reminder_emails = serializers.BooleanField(source='profile.reminder_emails', default=True)
    daily_emails = serializers.BooleanField(source='profile.daily_emails', default=True)

    class Meta:
        model = User
        fields = ('pk', 'username', 'first_name', 'last_name', 'email', 'email2', 'avatar',
                  'about', 'location', 'reminder_emails', 'daily_emails')

    def create(self, validated_data):
        profile_data = validated_data.pop('profile', None)
        user = super(UserSerializer, self).create(validated_data)
        self.update_or_create_profile(user, profile_data)
        return user

    def update(self, instance, validated_data):
        profile_data = validated_data.pop('profile', None)
        self.update_or_create_profile(instance, profile_data)
        return super(UserSerializer, self).update(instance, validated_data)

    def update_or_create_profile(self, user, profile_data):
        # This always creates a Profile if the User is missing one;
        # change the logic here if that's not right for your app
        Profile.objects.update_or_create(user=user, defaults=profile_data)


class PublicUserSerializer(serializers.ModelSerializer):
    about = serializers.CharField(source='profile.about', required=False)
    location = serializers.CharField(source='profile.location', required=False)
    avatar = ImageField(source='profile.avatar', required=False, allow_null=True, read_only=True)

    class Meta:
        model = User
        fields = ('pk', 'username', 'about', 'location', 'avatar')


class AdminUserSerializer(serializers.ModelSerializer):
    email2 = serializers.EmailField(source='profile.email2')
    has_paid = serializers.BooleanField(source='profile.has_paid', default=True)
    open_bettables = serializers.SerializerMethodField(read_only=True)
    avatar = ImageField(source='profile.avatar')

    class Meta:
        model = User
        fields = ('pk', 'username', 'email', 'email2', 'first_name', 'last_name', 'avatar', 'has_paid', 'is_active', 'open_bettables', 'last_login')

    def get_open_bettables(self, obj):
        return len(obj.profile.get_open_bettables())

    def update(self, instance, validated_data):
        profile_data = validated_data.pop('profile', None)
        Profile.objects.filter(user=instance).update(has_paid=profile_data['has_paid'])
        return super(AdminUserSerializer, self).update(instance, validated_data)


class PostSerializer(serializers.ModelSerializer):
    author_details = PublicUserSerializer(source='author', read_only=True)
    no_comments = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Post
        fields = '__all__'
        extra_kwargs = {
            'author': {'write_only': True},
            'as_mail': {'write_only': True},
            'force_active_users': {'write_only': True},
            'force_inactive_users': {'write_only': True},
            'force_all_users': {'write_only': True}
        }

    def get_no_comments(self, obj):
        return obj.comments.count()

    def validate(self, attrs):
        if attrs['finished'] and not attrs['title']:
            raise serializers.ValidationError({'title': 'Dieses Feld darf nicht leer sein.'})
        if attrs['finished'] and not attrs['content']:
            raise serializers.ValidationError({'content': 'Dieses Feld darf nicht leer sein.'})
        return attrs


class CommentSerializer(serializers.ModelSerializer):
    author_details = PublicUserSerializer(source='author', read_only=True)
    no_replies = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Comment
        exclude = ('author',)  # always set to the request's user

    def get_no_replies(self, obj):
        replies = obj.replies

        count = 0
        if replies.count() > 0:
            count += replies.count()
            for reply in replies.iterator():
                count += self.get_no_replies(reply)
        return count


class StatisticSerializer(serializers.ModelSerializer):
    username = CharField(source='user.username', read_only=True)
    user_avatar = CharField(source='user.profile.avatar', read_only=True)

    class Meta:
        model = Statistic
        fields = '__all__'


