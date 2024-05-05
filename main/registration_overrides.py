# # -*- coding: utf-8 -*-
import re
from string import whitespace, ascii_letters

from django.conf import settings
from django.contrib.sites.requests import RequestSite
from django.core import validators
from django.core.mail.message import EmailMultiAlternatives
from django.template.loader import render_to_string
from dj_rest_auth.registration.serializers import RegisterSerializer
from dj_rest_auth.serializers import PasswordResetConfirmSerializer, PasswordResetSerializer, PasswordChangeSerializer
from rest_framework import serializers
from rest_framework import status
from rest_framework.response import Response

from main.login_overrides import RtgObtainJSONWebToken
from main.mail_utils import with_rtg_template

ADDITIONAL_USERNAME_CHARACTERS = 'äöüÄÖÜéèáàß.@+-'
USERNAME_CHARACTERS = ascii_letters + whitespace + ADDITIONAL_USERNAME_CHARACTERS
USERNAME_REGEX = r'^[\w\s' + ADDITIONAL_USERNAME_CHARACTERS + ']+$'


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
    regex = USERNAME_REGEX
    message = 'Dein Username darf nur aus Buchstaben, Zahlen, Leerzeichen und @/./+/-/_. bestehen.'
    flags = re.ASCII


rtg_username_validators = [RtgUsernameValidator()]


class RtgRegisterView(RtgObtainJSONWebToken):

    def post(self, request, *args, **kwargs):
        if not settings.REGISTRATION_OPEN:
            return Response(
                {"error": "Die Registrierung für die RTG ist geschlossen."},
                status=status.HTTP_403_FORBIDDEN
            )

        # the RegisterSerializer expects the two passwords to be in fields named password1 and password2
        # However, the JWT serializer later on expects a password field to be present
        # We'd like to send the schema password/password2 in the payload, so we need to enhance the
        # serialized and validated data with password1 here in order to satisfy the RegisterSerializer
        request_data_with_password1_field = {**request.data, **{'password1': request.data['password']}}

        serializer = RtgRegisterSerializer(data=request_data_with_password1_field)
        serializer.is_valid(raise_exception=True)
        user = serializer.save(self.request)

        site = RequestSite(request)
        RtgRegisterView.send_mail_to_user(user)
        if not settings.DEBUG:
            RtgRegisterView.send_mail_to_staff(site, user)

        return super(RtgRegisterView, self).post(request)

    @staticmethod
    def send_mail_to_staff(site, new_user):
        subject = '%sNeue Registrierung von %s (%s)' % (settings.EMAIL_PREFIX, new_user.get_full_name(), new_user.username)
        text_content = render_to_string('registration/activation_email_staff.html', {'user': new_user, 'site': site})
        html_content = with_rtg_template({'subtitle': 'Neues Mitglied', 'content': text_content})

        mail = EmailMultiAlternatives(subject, text_content, settings.DEFAULT_FROM_EMAIL, to=[settings.DEFAULT_STAFF_EMAIL])
        mail.attach_alternative(html_content, "text/html")
        mail.send()

    @staticmethod
    def send_mail_to_user(new_user):
        subject = '%sWillkommen in der Royalen Tippgemeinschaft' % settings.EMAIL_PREFIX
        text_content = render_to_string('registration/registration_confirm_email.txt', {'user': new_user})
        html_content = with_rtg_template({'subtitle': 'Herzlich Willkommen', 'content': text_content})
        admin_recipients = [tpl[1] for tpl in settings.ADMINS]

        mail = EmailMultiAlternatives(subject, text_content, settings.DEFAULT_FROM_EMAIL, [new_user.email],
                                      bcc=admin_recipients)
        mail.attach_alternative(html_content, "text/html")
        mail.send()


rtg_register = RtgRegisterView.as_view()


# TODO P3 it seems the password validation here is different than on register
# on register it needs to be 8 characters long, but here it may be shorter?
class RtgPasswordChangeSerializer(PasswordChangeSerializer):
    def validate_old_password(self, value):
        try:
            return super(RtgPasswordChangeSerializer, self).validate_old_password(value)
        except serializers.ValidationError:
            raise serializers.ValidationError('Ungültiges aktuelles Passwort')


class RtgPasswordResetSerializer(PasswordResetSerializer):
    def get_email_options(self):
        return {
            'extra_email_context': {
                'site_base_url': settings.SITE_BASE_URL
            }
        }


class RtgPasswordResetConfirmSerializer(PasswordResetConfirmSerializer):

    new_password1 = serializers.CharField(min_length=6, max_length=128)
    new_password2 = serializers.CharField(min_length=6, max_length=128)
