# # -*- coding: utf-8 -*-

from django.conf import settings
from django.contrib.auth import user_logged_in
from rest_framework import status
from rest_framework.response import Response
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView


class RtgTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super(RtgTokenObtainPairSerializer, cls).get_token(user)

        last_login = None
        if user:
            last_login = user.last_login
            user_logged_in.send(sender=user.__class__, user=user)

        token['username'] = user.username
        token['admin'] = user.is_staff
        token['has_paid'] = user.profile.has_paid
        token['avatar'] = str(user.profile.avatar)
        token['no_open_bets'] = len(user.profile.get_open_bettables()),
        token['last_login'] = last_login.isoformat() if last_login else None

        return token


class RtgObtainJSONWebToken(TokenObtainPairView):
    serializer_class = RtgTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        if not settings.LOGIN_OPEN:
            return Response(
                {"error": "Es tut uns Leid, der Login ist aktuell leider nicht möglich."},
                status=status.HTTP_403_FORBIDDEN
            )

        return super(TokenObtainPairView, self).post(request)
