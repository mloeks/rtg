# # -*- coding: utf-8 -*-

from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework_jwt.views import ObtainJSONWebToken


class RtgObtainJSONWebToken(ObtainJSONWebToken):
    def post(self, request, *args, **kwargs):
        if not settings.LOGIN_OPEN:
            return Response(
                {"error": "Es tut uns Leid, der Login ist aktuell leider nicht möglich."},
                status=status.HTTP_403_FORBIDDEN
            )

        return super(ObtainJSONWebToken, self).post(request)


rtg_obtain_jwt_token = RtgObtainJSONWebToken.as_view()
