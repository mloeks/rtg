# -*- coding: utf-8 -*-
from django.template.defaultfilters import filesizeformat, lower
from rest_framework import serializers
from rest_framework.fields import CharField, IntegerField

from main.models import *
from .fields import Base64ImageField


class BetSerializer(serializers.ModelSerializer):
    # needs to be specified explicitly with default because it is part of a unique_together relation in the model
    user = serializers.PrimaryKeyRelatedField(read_only=True, default=serializers.CurrentUserDefault())

    bettable_type = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Bet
        exclude = ('result_bet_type',)

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
        extra_kwargs = {
            'points': {'write_only': True}
        }

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

    hometeam_name = serializers.CharField(source='hometeam.name', read_only=True)
    awayteam_name = serializers.CharField(source='awayteam.name', read_only=True)

    class Meta:
        model = Game
        fields = ('kickoff', 'deadline', 'hometeam', 'hometeam_name', 'awayteam', 'awayteam_name',
                  'homegoals', 'awaygoals', 'city', 'round', 'round_details', 'venue', 'bets_open')
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


class UserSerializer(serializers.ModelSerializer):
    profile_id = IntegerField(source='profile.pk', read_only=True)

    email = serializers.EmailField(allow_blank=False)

    class Meta:
        model = User
        fields = ('pk', 'username', 'first_name', 'last_name', 'email', 'profile_id')

    def create(self, validated_data):
        user = User.objects.create(**validated_data)
        return user


class ProfileSerializer(serializers.ModelSerializer):
    avatar_cropped = Base64ImageField(required=False)

    class Meta:
        model = Profile
        fields = ('pk', 'email2', 'location', 'about', 'reminder_emails', 'daily_emails', 'avatar', 'avatar_cropped')

    def validate(self, attrs):
        if 'avatar' in attrs:
            avatar = attrs['avatar']
            if avatar and len(avatar) > settings.MAX_UPLOAD_SIZE:
                raise ValidationError('Bitte ein Bild mit max. %s hochladen.' % filesizeformat(settings.MAX_UPLOAD_SIZE))
        if 'avatar_cropped' in attrs:
            avatar_cropped = attrs['avatar_cropped']
            if avatar_cropped and len(avatar_cropped) > settings.MAX_UPLOAD_SIZE:
                raise ValidationError('Bitte ein Bild mit max. %s hochladen.' % filesizeformat(settings.MAX_UPLOAD_SIZE))

        return attrs


class PublicProfileSerializer(serializers.ModelSerializer):
    user_pk = IntegerField(source='user.pk', read_only=True)
    username = CharField(source='user.username', read_only=True)

    class Meta:
        model = Profile
        fields = ('pk', 'location', 'about', 'avatar_cropped', 'user_pk', 'username')


class AdminProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ('pk', 'email2', 'location', 'about', 'has_paid', 'avatar_cropped')


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


