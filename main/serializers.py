# -*- coding: utf-8 -*-
from django.template.defaultfilters import filesizeformat, lower
from rest_framework import serializers
from rest_framework.fields import CharField, IntegerField

import registration_overrides
from main.models import *
from .fields import Base64ImageField


class BetSerializer(serializers.ModelSerializer):
    # needs to be specified explicitly with default because it is part of a unique_together relation in the model
    user = serializers.PrimaryKeyRelatedField(read_only=True, default=serializers.CurrentUserDefault())

    bettable_type = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Bet
        exclude = ('result_bet_type',)
        read_only_fields = ('points',)

    def get_bettable_type(self, obj):
        return lower(type(obj.bettable.get_related_child()).__name__)

    def validate(self, attrs):
        if attrs['bettable'].deadline_passed():
            raise ValidationError('Die Deadline ist bereits abgelaufen.')
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
        fields = ('name', 'abbreviation')

    @staticmethod
    def as_dict(obj):
        return {
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


# Combining custom Profile with User, cf. https://stackoverflow.com/a/28733782
class UserSerializer(serializers.ModelSerializer):
    # TODO P3 where does the min_length 3 requirement actually come from?
    username = serializers.CharField(validators=registration_overrides.rtg_username_validators,
                                     min_length=3, max_length=150)
    email = serializers.EmailField(allow_blank=False)
    email2 = serializers.EmailField(source='profile.email2', required=False, allow_blank=True)
    avatar = Base64ImageField(source='profile.avatar', required=False, allow_null=True)
    avatar_cropped = Base64ImageField(source='profile.avatar_cropped', required=False, allow_null=True)
    about = serializers.CharField(source='profile.about', required=False, allow_blank=True)
    location = serializers.CharField(source='profile.location', required=False, allow_blank=True)
    reminder_emails = serializers.BooleanField(source='profile.reminder_emails', default=True)
    daily_emails = serializers.BooleanField(source='profile.daily_emails', default=True)

    class Meta:
        model = User
        fields = ('pk', 'username', 'first_name', 'last_name', 'email', 'email2', 'avatar', 'avatar_cropped',
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

    # TODO P1 check if this still works for avatar uploads
    # def validate(self, attrs):
    #     if 'avatar' in attrs:
    #         avatar = attrs['avatar']
    #         if avatar and len(avatar) > settings.MAX_UPLOAD_SIZE:
    #             raise ValidationError('Bitte ein Bild mit max. %s hochladen.' % filesizeformat(settings.MAX_UPLOAD_SIZE))
    #     if 'avatar_cropped' in attrs:
    #         avatar_cropped = attrs['avatar_cropped']
    #         if avatar_cropped and len(avatar_cropped) > settings.MAX_UPLOAD_SIZE:
    #             raise ValidationError('Bitte ein Bild mit max. %s hochladen.' % filesizeformat(settings.MAX_UPLOAD_SIZE))
    #
    #     return attrs


class PublicUserSerializer(serializers.ModelSerializer):
    about = serializers.CharField(source='profile.about', required=False)
    location = serializers.CharField(source='profile.location', required=False)
    avatar_cropped = Base64ImageField(source='profile.avatar_cropped', required=False)

    class Meta:
        model = User
        fields = ('pk', 'username', 'about', 'location', 'avatar_cropped')


class AdminUserSerializer(serializers.ModelSerializer):
    has_paid = serializers.BooleanField(source='profile.has_paid', default=True)

    class Meta:
        model = User
        fields = ('pk', 'username', 'first_name', 'last_name', 'has_paid')


class PostSerializer(serializers.ModelSerializer):
    author_name = CharField(source='author.username', read_only=True)

    class Meta:
        model = Post
        fields = '__all__'
        extra_kwargs = {
            'author': {'write_only': True},
            'as_mail': {'write_only': True},
            'force_mail': {'write_only': True}
        }


class StatisticSerializer(serializers.ModelSerializer):
    username = CharField(source='user.username', read_only=True)

    class Meta:
        model = Statistic
        fields = '__all__'


