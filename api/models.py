from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from api.validators import CustomUnicodeUsernameValidator


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self):
        pass

    def create_superuser(self):
        pass


class User(AbstractBaseUser, PermissionsMixin):
    # TODO: id
    username_validator = CustomUnicodeUsernameValidator()
    username = models.CharField(
        _('username'),
        max_length=50,
        unique=True,
        help_text=_('Required. 50 characters or fewer. Letters, digits and @/./+/-/_ only.'),
        validators=[username_validator],
        error_messages={
            'unique': _("A user with that username already exists."),
        },
    )
    first_name = models.CharField(_('first name'), max_length=150, blank=True)
    second_name = models.CharField(_('second name'), max_length=150, blank=True)
    patronymic = models.CharField(_('patronymic'), max_length=150, blank=True)
    SEX_CHOICES = [
        ('m', "male"),
        ('f', "female")
    ]
    sex = models.CharField(max_length=1, choices=SEX_CHOICES)  # TODO: Согласовать добавление пола
    email = models.EmailField(
        _('email address'),
        unique=True,
        error_messages={
            'unique': _("A user with that email already exists."),
        },
    )
    phone = models.CharField(
        _('phone number'),
        unique=True,
        error_messages={
            'unique': _("A user with that phone number already exists."),
        },
    )
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('')  # TODO: Что Никита имел ввиду под этим полем?
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        )
    )
    is_superuser = models.BooleanField(
        _('superuser'),
        default=False,
        help_text=_(
            'This field indicates whether the user has superuser rights'
        )
    )
    objects = UserManager()

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []  # TODO: !!


class Student(models.Model):
    # TODO: id
    year_of_enrollment = models.CharField(_('year of enrollment'), max_length=4, blank=False)
    record_book_number = models.CharField(_('number of student record book'), max_length=20, blank=True)
    user = models.ForeignKey("User", on_delete=models.CASCADE, related_name='student', blank=False, null=False)
    courseGroup = models.ForeignKey(
        "CourseGroup",
        on_delete=models.CASCADE,
        related_name='student group',
        blank=False, null=False)


class Professor(models.Model):
    # TODO: id
    department = models.CharField(_('professor department'), max_length=50, blank=False)
    user = models.ForeignKey("User", on_delete=models.CASCADE, related_name='professor', blank=False, null=False)


class CourseGroup(models.Model):
    # TODO: id
    course_number = models.IntegerField(_('number of course'), blank=False)
    group_number = models.CharField(_('number of group'), blank=False)
    EDUCATION_LEVELS = [
        ('b', "bachelor"),
        ('m', "magistracy"),
        ('p', "postgraduate"),
        ('s', "specialty")
    ]
    higher_education_level = models.CharField(
        _('level of higher education'),
        max_length=1, choices=EDUCATION_LEVELS, blank=True)


class Map(models.Model):
    # TODO: id
    BUILDINGS = [
        ('')  # TODO: заполнить enum
    ]
    building = models.CharField(_('building'), max_length=50, choices=BUILDINGS, blank=True)
    building_level = models.IntegerField(_('level of building'), max_length=1, choices=BUILDINGS)
    map_file = models.FilePathField()  # TODO: !


class Message(models.Model):
    # TODO: id
    text = models.CharField(_('message text'), max_length=1000, blank=False)
    message_datetime = models.DateTimeField(_('message datetime'), default=timezone.now)
    user_from = models.ForeignKey("User", on_delete=models.DO_NOTHING, related_name='massageFrom', blank=False,
                                  null=False)
    user_to = models.ForeignKey("User", on_delete=models.DO_NOTHING, related_name='messageTo', blank=False, null=False)


class Schedule(models.Model):
    # TODO: id
    schedule_file = models.FilePathField()  # TODO: !
    course_group = models.ForeignKey("CourseGroup",
                                     on_delete=models.DO_NOTHING, related_name='schedule', blank=False, null=False)


class Event(models.Model):
    # TODO: id
    title = models.CharField(
        _('event title'),
        max_length=100,
        blank=True
    )
    description = models.CharField(
        _('event description'),
        max_length=1000,
        blank=True
    )
    event_datetime = models.DateTimeField(_('event datetime'), default=timezone.now)


class Publication(models.Model):
    # TODO: id
    title = models.CharField(
        _('publication title'),
        max_length=100,
        blank=True
    )
    body_text = models.CharField(
        _('publication text'),
        max_length=1500,
        blank=True
    )
    publication_datetime = models.DateTimeField(_('publication datetime'), default=timezone.now)
    event = models.ForeignKey("Event", on_delete=models.DO_NOTHING, related_name='publication', blank=True,
                              null=True)
