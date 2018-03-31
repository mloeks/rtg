# # -*- coding: utf-8 -*-
import re

from django.conf import settings
from django.contrib.sites.requests import RequestSite
from django.core import validators
from django.core.mail import send_mail
from django.core.mail.message import EmailMultiAlternatives
from django.template.loader import render_to_string
from rest_auth.registration.serializers import RegisterSerializer
from rest_auth.serializers import PasswordResetConfirmSerializer
from rest_framework import serializers
from rest_framework import status
from rest_framework.response import Response
from rest_framework_jwt.views import ObtainJSONWebToken

from main.utils import merge_two_dicts


class RtgRegisterSerializer(RegisterSerializer):
    """
    Serializer for rest-auth registration. Include user's first and last name as mandatory fields (RTG needs to know).
    """
    first_name = serializers.CharField(required=True, min_length=2)
    last_name = serializers.CharField(required=True, min_length=2)
    email = serializers.EmailField(required=True)

    def get_cleaned_data(self):
        return {
            'username': self.validated_data.get('username', ''),
            'password': self.validated_data.get('password1', ''),
            'password1': self.validated_data.get('password1', ''),
            'password2': self.validated_data.get('password2', ''),
            'email': self.validated_data.get('email', ''),
            'first_name': self.validated_data.get('first_name', ''),
            'last_name': self.validated_data.get('last_name', '')
        }


class RtgUsernameValidator(validators.RegexValidator):
    regex = r'^[\w\säöüÄÖÜéèáàß.@+-]+$'
    message = 'Dein Username darf nur aus Buchstaben, Zahlen, Leerzeichen und @/./+/-/_. bestehen.'
    flags = re.ASCII


rtg_username_validators = [RtgUsernameValidator()]


class RtgRegisterView(ObtainJSONWebToken):

    def post(self, request, *args, **kwargs):
        if not settings.REGISTRATION_OPEN:
            return Response(
                {"error": "Es tut uns Leid, aber die Registrierung für die RTG ist aktuell nicht möglich."},
                status=status.HTTP_403_FORBIDDEN
            )

        # the RegisterSerializer expects the two passwords to be in fields named password1 and password2
        # However, the JWT serializer later on expects a password field to be present
        # We'd like to send the schema password/password2 in the payload, so we need to enhance the
        # serialized and validated data with password1 here in order to satisfy the RegisterSerializer
        request_data_with_password1_field = merge_two_dicts(request.data, {'password1': request.data['password']})

        # This does only work from Python 3.5 upwards
        # request_data_with_password1_field = {**request.data, **{'password1': request.data['password']}}

        serializer = RtgRegisterSerializer(data=request_data_with_password1_field)
        serializer.is_valid(raise_exception=True)
        user = serializer.save(self.request)

        site = RequestSite(request)
        self.send_confirmation_mails(site, user)

        return super(RtgRegisterView, self).post(request)

    def send_confirmation_mails(self, site, new_user):
        # send notification mail to staff members
        ctx = {'user': new_user, 'site': site}
        subject = render_to_string('registration/activation_email_staff_subject.txt', ctx)
        # Email subject *must not* contain newlines
        subject = ''.join(subject.splitlines())
        subject = settings.EMAIL_PREFIX + subject
        message = render_to_string('registration/activation_email_staff.html', ctx)

        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [settings.DEFAULT_STAFF_EMAIL])

        # send confirmation mail to new user
        subject = '%sWillkommen in der Royalen Tippgemeinschaft' % settings.EMAIL_PREFIX
        message = render_to_string('registration/registration_confirm_email.txt', {'user': new_user})
        admin_recipients = [tpl[1] for tpl in settings.ADMINS]

        mail = EmailMultiAlternatives(subject, message, settings.DEFAULT_FROM_EMAIL, [new_user.email],
                                      bcc=admin_recipients)
        mail.send()

rtg_register = RtgRegisterView.as_view()


class RtgPasswordResetConfirmSerializer(PasswordResetConfirmSerializer):

    new_password1 = serializers.CharField(min_length=6, max_length=128)
    new_password2 = serializers.CharField(min_length=6, max_length=128)
