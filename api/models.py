import os
from datetime import datetime, timedelta

import jwt
from django.conf import settings
from django.contrib import auth
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.core.validators import FileExtensionValidator, MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from phonenumber_field.modelfields import PhoneNumberField

from pytils.translit import slugify

from api.storage import OverwriteStorage
from api.validators import CustomUnicodeUsernameValidator, FileValidator


def transliterate_filename(filename):
    name, ext = os.path.splitext(filename)
    name = slugify(name)
    return f'{name}{ext}'


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
        _('Логин'),
        max_length=50,
        unique=True,
        help_text=_('Required. 50 characters or fewer. Letters, digits and @/./+/-/_ only.'),
        validators=[username_validator],
        error_messages={
            'unique': _("A user with that username already exists."),
        },
    )
    # user_image = models.ImageField() //TODO: image upload
    first_name = models.CharField(_('Имя'), max_length=20, blank=True)
    second_name = models.CharField(_('Фамилия'), max_length=20, blank=True)
    patronymic = models.CharField(_('Отчество'), max_length=20, blank=True)
    email = models.EmailField(
        _('Адрес электронной почты'),
        unique=True,
        error_messages={
            'unique': _("A user with that email already exists."),
        },
    )
    phone = PhoneNumberField(
        _('Номер телефона'),
        unique=True,
        null=True,
        blank=True
    )
    is_staff = models.BooleanField(
        _('Стафф'),
        default=False,
        help_text=_(
            'Аккаунт работника')
    )
    is_active = models.BooleanField(
        _('Активный'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        )
    )
    is_verified = models.BooleanField(
        _('Подтвержденный'),
        default=False,
        # help_text=_() TODO: заполнить
    )

    def get_image_path(self, filename):
        name, ext = os.path.splitext(filename)
        path = f'avatars/{self.username}{ext}'
        return path

    avatar = models.ImageField(
        _('Изображение пользователя'),
        null=True,
        blank=True,
        upload_to=get_image_path,
        validators=[
            FileExtensionValidator(['png', 'jpg', 'gif', 'jpeg'])
        ]
    )

    objects = UserManager()

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']


@receiver(pre_save, sender=User)
def delete_old_avatar(sender, instance, **kwargs):
    if instance.pk:
        try:
            old_instance = User.objects.get(pk=instance.pk)
            if old_instance.avatar != instance.avatar:
                old_instance.avatar.delete(save=False)
        except User.DoesNotExist:
            pass

    # def token(self):
    #     return self._generate_jwt_token()
    #
    # def _generate_jwt_token(self):
    #     dt = datetime.now() + timedelta(days=1)
    #
    #     token = jwt.encode({
    #         'id': self.pk,
    #         'exp': int(dt.strftime('%s'))
    #     }, settings.SECRET_KEY, algorithm='HS256')
    #
    #     return token.decode('utf-8')


class Student(models.Model):
    year_of_enrollment = models.CharField(_('Год поступления'), max_length=4, blank=False)
    record_book_number = models.CharField(_('Номер зачетной книжки'), max_length=20, blank=True)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        verbose_name=_("User"),
        on_delete=models.CASCADE,
        related_name='student',
        blank=False, null=False)
    course_group = models.ForeignKey(
        "CourseGroup",
        on_delete=models.DO_NOTHING,
        related_name='student_group',
        blank=True, null=True)


class Professor(models.Model):
    department = models.CharField(_('Кафедра'), max_length=50, blank=False)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        verbose_name=_("User"),
        on_delete=models.CASCADE,
        related_name='professor',
        blank=False, null=False)


class CourseGroup(models.Model):
    course_number = models.IntegerField(_('Номер курса'), blank=False,
                                        validators=[MinValueValidator(1), MaxValueValidator(5)])
    group_number = models.CharField(_('Номер группы'), max_length=10, blank=False)  # TODO: валидация двух полей
    EDUCATION_LEVELS = [
        ('b', "bachelor"),
        ('m', "magistracy"),
        ('p', "postgraduate"),
        ('s', "specialty")
    ]
    EDUCATION_LEVELS_RU = {
        'b': "бакалавриат",
        'm': "магистратура",
        'p': "аспирантура",
        's': "специалитет"
    }
    higher_education_level = models.CharField(
        _('Ступень высшего образования'),
        max_length=1, choices=EDUCATION_LEVELS, blank=True)

    def __str__(self):
        return f"{self.course_number} курс {self.group_number} группа {self.EDUCATION_LEVELS_RU[self.higher_education_level]}"


class Map(models.Model):
    # TODO: https://stackoverflow.com/questions/16041232/django-delete-filefield

    def get_map_path(self, filename):
        path = f'maps/{self.building}_{self.building_level}.png'
        return path

    BUILDINGS = [
        ('m', "main building"),
        ('ex1a', "extension building 1A"),
        ('ex1b', "extension building 1B"),
    ]

    BUILDINGS_RU = [
        ('m', "Главный корпус"),
        ('ex1a', "Пристройка 1А"),
        ('ex1b', "Пристройка 1Б"),
    ]
    BUILDINGS_RU_DICT = {
        'm': "Главный корпус",
        'ex1a': "Пристройка 1А",
        'ex1b': "Пристройка 1Б"
    }

    building = models.CharField(_('Строение'), max_length=4, choices=BUILDINGS, blank=True)
    building_level = models.IntegerField(_('Этаж строения'))
    map_file = models.FileField(upload_to=get_map_path,
                                validators=[
                                    FileExtensionValidator(['png'])
                                ], blank=True, null=True)

    def __str__(self):
        return f"{self.BUILDINGS_RU_DICT[self.building]} {self.building_level} этаж"


# class Message(models.Model):
#     text = models.CharField(_('message text'), max_length=100, blank=False)
#     message_datetime = models.DateTimeField(_('message datetime'), default=timezone.now)
#     user_from = models.ForeignKey(
#         settings.AUTH_USER_MODEL,
#         verbose_name=_("User"), on_delete=models.DO_NOTHING,
#         related_name='massageFrom',
#         blank=False, null=False)
#     user_to = models.ForeignKey(
#         settings.AUTH_USER_MODEL,
#         verbose_name=_("User"), on_delete=models.DO_NOTHING,
#         related_name='messageTo',
#         blank=False, null=False)


class Schedule(models.Model):

    def get_schedule_path(self, filename):
        path = f'schedules/' \
               f'{self.course_group.course_number}_' \
               f'{self.course_group.group_number}_' \
               f'{self.course_group.higher_education_level}.json'
        return path

    course_group = models.ForeignKey("CourseGroup",
                                     on_delete=models.DO_NOTHING, related_name='schedule', blank=False, null=False)
    schedule_file = models.FileField(_('Файл расписания'), upload_to=get_schedule_path,
                                     validators=[
                                         FileExtensionValidator(['json']),
                                         FileValidator(1024 * 100)
                                     ],
                                     storage=OverwriteStorage(),
                                     max_length=50)

    def __str__(self):
        return f"Расписание для {self.course_group}"


class Event(models.Model):
    title = models.CharField(
        _('Название события'),
        max_length=100,
        blank=True
    )
    description = models.TextField(
        _('Описание события'),
        max_length=800,
        blank=True
    )

    event_start_datetime = models.DateTimeField(_('Начало события'), default=timezone.now)
    event_end_datetime = models.DateTimeField(_('Конец события'), default=timezone.now)
    is_full_day = models.BooleanField(
        _('Полный день'),
        default=True,
    )
    course_groups = models.ManyToManyField(
        "CourseGroup",
        blank=True,
        default=None,
        symmetrical=False,
        related_name="group_events"
    )

    EVENT_TYPES_RU = [
        ('i', "Информация"),
        ('e', "Экзамен"),
        ('a', "Аттестация"),
        ('h', "Праздник"),
    ]

    e_type = models.CharField(_("Тип события"), max_length=1, choices=EVENT_TYPES_RU, blank=False, null=False)

    def __str__(self):
        return self.title


class Publication(models.Model):
    title = models.CharField(
        _('Название публикации'),
        max_length=100,
        blank=True
    )
    body_text = models.TextField(
        _('Текст публикации'),
        max_length=2000,
        blank=True
    )
    publication_datetime = models.DateTimeField(_('Время публикации'), default=timezone.now)
    event = models.ForeignKey("Event", on_delete=models.DO_NOTHING, related_name='publication', blank=True,
                              null=True)

    image = models.CharField(_('Изображение'),
                             blank=True, null=True)

    def __str__(self):
        return self.title

