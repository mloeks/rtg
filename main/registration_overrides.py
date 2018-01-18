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
            'password': self.validated_data.get('password', ''),
            'password1': self.validated_data.get('password', ''),
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
        request_data_with_password1_field = {**request.data, **{'password1': request.data['password']}}

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
        subject = '%sDeine Registrierung bei der RTG 2016' % settings.EMAIL_PREFIX
        message = render_to_string('registration/registration_confirm_email.txt', {'user': new_user})
        admin_recipients = [tpl[1] for tpl in settings.ADMINS]

        mail = EmailMultiAlternatives(subject, message, settings.DEFAULT_FROM_EMAIL, [new_user.email],
                                      bcc=admin_recipients)
        mail.send()

rtg_register = RtgRegisterView.as_view()


class RtgPasswordResetConfirmSerializer(PasswordResetConfirmSerializer):

    new_password1 = serializers.CharField(min_length=6, max_length=128)
    new_password2 = serializers.CharField(min_length=6, max_length=128)

#
# ## custom registration view
# class RtgRegistrationView(RegistrationView):
#
#     @csrf_protect
#     def register(self, request, **cleaned_data):
#         username, email, password = cleaned_data['username'], cleaned_data['email'], cleaned_data['password1']
#         first_name, last_name = cleaned_data['first_name'], cleaned_data['last_name']
#
#         site = RequestSite(request)
#         new_user = RtgRegistrationProfile.objects.create_inactive_rtg_user(site, username, first_name, last_name, email,
#                                                                            password)
#         # signal können wir uns sparen (?)
#         # signals.user_registered.send(sender=self.__class__,
#         #                              user=new_user,
#         #                              request=request)
#
#         return new_user
#
#
# class RtgRegistrationManager(RegistrationManager):
#     def create_inactive_rtg_user(self, site, username, first_name, last_name, email, password):
#         new_user = User.objects.create_user(username, email, password, first_name=first_name, last_name=last_name)
#         new_user.is_active = False
#         new_user.save()
#         # maybe edit profile fields
#         # new_user.profile.save()
#
#         self.send_confirmation_mails(site, new_user)
#
#         return new_user
#
#     def send_confirmation_mails(self, site, new_user):
#         # send notification mail to staff members
#         ctx = {'user': new_user, 'site': site}
#         subject = render_to_string('registration/activation_email_staff_subject.txt', ctx)
#         # Email subject *must not* contain newlines
#         subject = ''.join(subject.splitlines())
#         message = render_to_string('registration/activation_email_staff.html', ctx)
#
#         staff_members = User.objects.filter(is_staff=True)
#         ## either to staff members registered e-mails or to configured default staff mail?
#         # send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, map(lambda it: it.email, staff_members))
#         send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [settings.DEFAULT_STAFF_EMAIL])
#
#         # send confirmation mail to new user
#         subject = _('Your registration at RTG 2014')
#         message = render_to_string('registration/registration_confirm_email.txt', {'user': new_user})
#
#         mail = EmailMultiAlternatives(subject, message, settings.DEFAULT_FROM_EMAIL, [new_user.email],
#                                       bcc=['admin@royale-tippgemeinschaft.de'])
#         mail.send()
#
#
# class RtgRegistrationProfile(RegistrationProfile):
#     objects = RtgRegistrationManager()
#
