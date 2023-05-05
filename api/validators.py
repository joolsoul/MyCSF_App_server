import re
from datetime import datetime

from django.core import validators
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers


@deconstructible
class CustomUnicodeUsernameValidator(validators.RegexValidator):
    regex = r'^[\w.+-]+\Z'
    message = _(
        'Enter a valid username. This value may contain only letters, '
        'numbers, and ./+/-/_ characters.'
    )
    flags = 0


def validate_year_of_enrollment(year_of_enrollment):
    if year_of_enrollment is None \
            or len(year_of_enrollment) != 4 \
            or int(year_of_enrollment) < 1990 \
            or int(year_of_enrollment) > int(datetime.now().year):
        raise serializers.ValidationError()


def validate_record_book_number(record_book_number):
    if record_book_number is None \
            or len(record_book_number) < 10:
        raise serializers.ValidationError()
