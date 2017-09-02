from django.contrib.auth.models import User
from django.core.validators import validate_email
from django.core.exceptions import ValidationError


class BasicBackend:
    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None


class EmailBackend(BasicBackend):
    def authenticate(self, username=None, password=None):
        try:
            validate_email(username)
            is_email = True
        except ValidationError:
            is_email = False

        if is_email:
            #If username is an email address, then try to pull it up
            try:
                user = User.objects.get(email__iexact=username)     # email is case-insensitive
            except User.DoesNotExist:
                return None
        else:
            #We have a non-email address username we should try username
            try:
                user = User.objects.get(username=username)          # username must match case sensitive
            except User.DoesNotExist:
                return None
        if user.check_password(password):
            return user
