from django.core.exceptions import ValidationError
import re


def game_result_validator(value):
    if not re.match('^[0-9]{1,2}:[0-9]{1,2}$', value):
        raise ValidationError('Game Result must be in the format x:x.')
