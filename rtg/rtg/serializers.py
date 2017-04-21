# -*- coding: utf-8 -*-
from django.contrib.auth.models import User, Group
from django.conf import settings as dj_settings
from django.template.defaultfilters import filesizeformat
from rest_framework.authtoken.models import Token
from rest_framework.fields import CharField, IntegerField, ImageField

from models import *
from rest_framework import serializers

from rtg.fields import Base64ImageField


class GameBetResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = GameBetResult


class GameBetSerializer(serializers.ModelSerializer):
    points = serializers.IntegerField(source='result_bet_type.points', read_only=True)

    # needs to be specified explicitly with default because it is part of a unique_together relation in the model
    user = serializers.PrimaryKeyRelatedField(read_only=True, default=serializers.CurrentUserDefault())

    class Meta:
        model = GameBet
        exclude = ('result_bet_type',)

    def validate(self, attrs):
        if attrs['game'].deadline_passed():
            raise ValidationError('Die Deadline ist bereits abgelaufen.')
        return attrs


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


class ExtraBetSerializer(serializers.ModelSerializer):
    points = serializers.SerializerMethodField()

    user = serializers.PrimaryKeyRelatedField(read_only=True, default=serializers.CurrentUserDefault())

    class Meta:
        model = ExtraBet

    def validate(self, attrs):
        if attrs['extra'].deadline_passed():
            raise ValidationError('Die Deadline ist bereits abgelaufen.')
        return attrs

    def get_points(self, obj):
        return obj.compute_points()


class TournamentGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = TournamentGroup
        fields = ('name', 'abbreviation')


class TournamentRoundSerializer(serializers.ModelSerializer):
    class Meta:
        model = TournamentRound
        fields = ('name', 'abbreviation', 'is_knock_out')


class TeamSerializer(serializers.ModelSerializer):
    group = TournamentGroupSerializer()

    class Meta:
        model = Team
        fields = ('id', 'name', 'abbreviation', 'group')


class VenueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Venue


class GameSerializer(serializers.ModelSerializer):
    city = CharField(source='venue.city', read_only=True)
    round = TournamentRoundSerializer()
    bets_open = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Game
        extra_kwargs = {
            'venue': {'write_only': True}
        }

    def get_bets_open(self, obj):
        return not obj.deadline_passed()


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
        extra_kwargs = {
            'author': {'write_only': True},
            'as_mail': {'write_only': True},
            'force_mail': {'write_only': True}
        }


class StatisticSerializer(serializers.ModelSerializer):
    username = CharField(source='user.username', read_only=True)

    class Meta:
        model = Statistic


