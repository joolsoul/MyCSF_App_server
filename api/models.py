from django.conf import settings
from django.contrib import auth
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField


from api.validators import CustomUnicodeUsernameValidator


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, username, email, password, **extra_fields):
        if not username:
            raise ValueError('The given username must be set')
        email = self.normalize_email(email)

        user = self.model(username=username, email=email, **extra_fields)
        user.password = make_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(username, email, password, **extra_fields)

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(username, email, password, **extra_fields)

    def with_perm(self, perm, is_active=True, include_superusers=True, backend=None, obj=None):
        if backend is None:
            backends = auth._get_backends(return_tuples=True)
            if len(backends) == 1:
                backend, _ = backends[0]
            else:
                raise ValueError(
                    'You have multiple authentication backends configured and '
                    'therefore must provide the `backend` argument.'
                )
        elif not isinstance(backend, str):
            raise TypeError(
                'backend must be a dotted import path string (got %r).'
                % backend
            )
        else:
            backend = auth.load_backend(backend)
        if hasattr(backend, 'with_perm'):
            return backend.with_perm(
                perm,
                is_active=is_active,
                include_superusers=include_superusers,
                obj=obj,
            )
        return self.none()


class User(AbstractBaseUser, PermissionsMixin):
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
    first_name = models.CharField(_('first name'), max_length=20, blank=True)
    second_name = models.CharField(_('second name'), max_length=20, blank=True)
    patronymic = models.CharField(_('patronymic'), max_length=20, blank=True)
    email = models.EmailField(
        _('email address'),
        unique=True,
        error_messages={
            'unique': _("A user with that email already exists."),
        },
    )
    phone = PhoneNumberField(
        _('phone number'),
        unique=True,
        null=True,
        blank=True
    )
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_(
            'Is staff account')
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        )
    )

    objects = UserManager()

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']


class Student(models.Model):
    year_of_enrollment = models.CharField(_('year of enrollment'), max_length=4, blank=False)
    record_book_number = models.CharField(_('number of student record book'), max_length=20, blank=True)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        verbose_name=_("User"),
        on_delete=models.CASCADE,
        related_name='student',
        blank=False, null=False)
    courseGroup = models.ForeignKey(
        "CourseGroup",
        on_delete=models.DO_NOTHING,
        related_name='student_group',
        blank=True, null=True)


class Professor(models.Model):
    department = models.CharField(_('professor department'), max_length=50, blank=False)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        verbose_name=_("User"),
        on_delete=models.CASCADE,
        related_name='professor',
        blank=False, null=False)


class CourseGroup(models.Model):
    course_number = models.IntegerField(_('number of course'), blank=False)
    group_number = models.CharField(_('number of group'), max_length=10, blank=False)
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
    BUILDINGS = [
        ('m', "main building"),
        ('ex', "extension building")
    ]
    building = models.CharField(_('building'), max_length=2, choices=BUILDINGS, blank=True)
    building_level = models.IntegerField(_('level of building'), choices=BUILDINGS)
    map_file = models.FilePathField()   # TODO: !


class Message(models.Model):
    text = models.CharField(_('message text'), max_length=100, blank=False)
    message_datetime = models.DateTimeField(_('message datetime'), default=timezone.now)
    user_from = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("User"), on_delete=models.DO_NOTHING,
        related_name='massageFrom',
        blank=False, null=False)
    user_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("User"), on_delete=models.DO_NOTHING,
        related_name='messageTo',
        blank=False, null=False)


class Schedule(models.Model):
    schedule_file = models.FilePathField()  # TODO: !
    course_group = models.ForeignKey("CourseGroup",
                                     on_delete=models.DO_NOTHING, related_name='schedule', blank=False, null=False)


class Event(models.Model):
    title = models.CharField(
        _('event title'),
        max_length=100,
        blank=True
    )
    description = models.CharField(
        _('event description'),
        max_length=800,
        blank=True
    )
    event_datetime = models.DateTimeField(_('event datetime'), default=timezone.now)


class Publication(models.Model):
    title = models.CharField(
        _('publication title'),
        max_length=100,
        blank=True
    )
    body_text = models.CharField(
        _('publication text'),
        max_length=800,
        blank=True
    )
    publication_datetime = models.DateTimeField(_('publication datetime'), default=timezone.now)
    event = models.ForeignKey("Event", on_delete=models.DO_NOTHING, related_name='publication', blank=True,
                              null=True)