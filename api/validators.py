import json
import re
from datetime import datetime

import jsonschema
from django.core import validators
from django.core.validators import BaseValidator
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.exceptions import ParseError, ValidationError
from . import schemas

from django.utils.deconstruct import deconstructible


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


def schedule_file_validate(schedule_file):
    try:
        jsonschema.validate(schedule_file, schemas.schedule)
    except ValueError:
        raise ParseError()


@deconstructible
class FileValidator(BaseValidator):
    def __call__(self, data):
        try:
            jsonschema.validate(json.load(data), schemas.schedule)
        except Exception as e:
            raise ValidationError("Ошибка валидации файла расписания")



