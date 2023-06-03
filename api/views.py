import datetime

from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils import timezone
from djoser import signals, utils
from djoser.conf import settings
from django.db.models import Q
from rest_framework import generics, status
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.mixins import RetrieveModelMixin, UpdateModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_429_TOO_MANY_REQUESTS
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet, GenericViewSet

from api.models import Student, Professor, CourseGroup, Schedule, Map, Event, Publication
from api.permissions import AdminOrReadOnlyPermission, IsOwnerOrAdmin
from api.schedule_utilities import get_user_schedule
from api.searchfilters import BuildingSearchFilter
from api.serializers import CourseGroupSerializer, MyUserCreateSerializer, SimpleUserSerializer, EventSerializer, \
    PublicationSerializer
from api.serializers import ScheduleSerializer, MapSerializer
from api.serializers import StudentCreateSerializer, ProfessorCreateSerializer

from rest_framework.pagination import LimitOffsetPagination

from api.throttle import ChatRateThrottle
from api.chat_bot import get_answer

User = get_user_model()


class ChatBotApiView(APIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [ChatRateThrottle]

    def post(self, request):
        try:
            ans_json = {'answer': get_answer(request.data['text'])}
            return Response(ans_json, status=HTTP_200_OK)
        except Exception as e:
            return Response({"answer": "Попробуйте позже"}, status=HTTP_429_TOO_MANY_REQUESTS)


class CourseGroupApiList(generics.ListCreateAPIView):
    queryset = CourseGroup.objects.all()
    serializer_class = CourseGroupSerializer
    permission_classes = [AdminOrReadOnlyPermission]


class EventApiView(ModelViewSet):
    permission_classes = [AdminOrReadOnlyPermission]
    queryset = Event.objects.all()
    serializer_class = EventSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_authenticated:
            queryset = queryset.filter(course_groups=None)
        elif self.request.user.is_superuser:
            pass
        else:
            try:
                student = self.request.user.student
                student_course_group = student.course_group
                queryset = queryset.filter(Q(course_groups=None) | Q(course_groups=student_course_group))
            except Exception as e:
                queryset = queryset.filter(course_groups=None)

        if self.request.query_params.get("latest") == "true":
            queryset = queryset.filter(event_start_datetime__gte=timezone.now()).order_by('event_start_datetime')
        return queryset


class PublicationApiList(generics.ListAPIView):
    queryset = Publication.objects.all()
    serializer_class = PublicationSerializer
    permission_classes = [AdminOrReadOnlyPermission]
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.order_by('-publication_datetime')
        return queryset


class MapApiView(ModelViewSet):
    permission_classes = [AdminOrReadOnlyPermission]
    queryset = Map.objects.all()
    serializer_class = MapSerializer
    filter_backends = [BuildingSearchFilter]
    search_fields = ['building']


class MapChoicesView(APIView):
    def get(self, request):
        serializer = MapSerializer()
        choices = serializer.fields['building'].choices

        use_ru_param = request.query_params.get('use_ru')
        if use_ru_param:
            choices_ru = {key: dict(Map.BUILDINGS_RU).get(key) for key in choices.keys()}
            return Response(choices_ru)
        else:
            return Response(choices)


class DateWeekInfoView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        date = request.query_params['date']
        parse_date = datetime.datetime.strptime(date, "%d-%m-%Y").date()
        response = {}
        week_number = parse_date.isocalendar().week
        weekday = parse_date.weekday()

        if week_number % 2 == 0:
            response['week'] = 'Знаменатель'
        else:
            response['week'] = 'Числитель'
        if weekday == 0:
            response['weekday'] = 'Понедельник'
        if weekday == 1:
            response['weekday'] = 'Вторник'
        if weekday == 2:
            response['weekday'] = 'Среда'
        if weekday == 3:
            response['weekday'] = 'Четверг'
        if weekday == 4:
            response['weekday'] = 'Пятница'
        if weekday == 5:
            response['weekday'] = 'Суббота'
        if weekday == 6:
            response['weekday'] = 'Воскресенье'

        return Response(response)


class UserScheduleViewSet(RetrieveModelMixin, GenericViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Schedule.objects.all()
    serializer_class = ScheduleSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        return Response(instance, status=HTTP_200_OK)

    def get_object(self):
        week = self.request.query_params.get('week')
        day = self.request.query_params.get('day')
        user_role = None
        user = None

        try:
            base_user = self.request.user
        except Exception:
            raise NotFound('user not found')
        err_count = 0

        try:
            student = base_user.student
            user_role = 'student'
            user = student
        except Exception:
            err_count += 1

        try:
            professor = base_user.professor
            user_role = 'professor'
            user = professor
        except Exception:
            err_count += 1

        if err_count >= 2:
            raise Exception('user dont load')

        return get_user_schedule(user, user_role, week, day)


# id - ignored
class UserShortInfoViewSet(RetrieveModelMixin, GenericViewSet):
    permission_classes = [IsAuthenticated]
    queryset = User.objects.all()
    serializer_class = MyUserCreateSerializer

    def get_object(self):
        try:
            _id = int(self.kwargs.get("pk"))
            if _id <= 0:
                return self.request.user
            else:
                return super().get_object()
        except Exception as e:
            print(e)
            return super().get_object()


# class StudentViewSet(UserViewSet):
#     # serializer_class = StudentCreateSerializer
#
#     def get_serializer_class(self):
#         if self.action == "create":
#             return StudentCreateSerializer
#         elif self.action == "destroy" or (
#             self.action == "me" and self.request and self.request.method == "DELETE"
#         ):
#             return settings.SERIALIZERS.user_delete
#         elif self.action == "activation":
#             return settings.SERIALIZERS.activation
#         elif self.action == "resend_activation":
#             return settings.SERIALIZERS.password_reset
#         elif self.action == "reset_password":
#             return settings.SERIALIZERS.password_reset
#         elif self.action == "reset_password_confirm":
#             if settings.PASSWORD_RESET_CONFIRM_RETYPE:
#                 return settings.SERIALIZERS.password_reset_confirm_retype
#             return settings.SERIALIZERS.password_reset_confirm
#         elif self.action == "set_password":
#             if settings.SET_PASSWORD_RETYPE:
#                 return settings.SERIALIZERS.set_password_retype
#             return settings.SERIALIZERS.set_password
#         elif self.action == "set_username":
#             if settings.SET_USERNAME_RETYPE:
#                 return settings.SERIALIZERS.set_username_retype
#             return settings.SERIALIZERS.set_username
#         elif self.action == "reset_username":
#             return settings.SERIALIZERS.username_reset
#         elif self.action == "reset_username_confirm":
#             if settings.USERNAME_RESET_CONFIRM_RETYPE:
#                 return settings.SERIALIZERS.username_reset_confirm_retype
#             return settings.SERIALIZERS.username_reset_confirm
#         elif self.action == "me":
#             return settings.SERIALIZERS.current_user
#
#         return self.serializer_class

class UserAvatarUpdateView(UpdateModelMixin, GenericViewSet):
    queryset = User.objects.all()
    serializer_class = SimpleUserSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        if 'avatar' in request.FILES:
            instance.avatar = request.FILES['avatar']
            instance.save()

        self.perform_update(serializer)

        return Response(serializer.data)

    def get_object(self):
        try:
            id = int(self.kwargs.get("pk"))
            if id <= 0:
                return self.request.user
            else:
                return super().get_object()
        except Exception as e:
            print(e)
            return super().get_object()


class ProfessorViewSet(ModelViewSet):
    serializer_class = ProfessorCreateSerializer
    queryset = Professor.objects.all()
    permission_classes = settings.PERMISSIONS.user
    token_generator = default_token_generator
    lookup_field = settings.USER_ID_FIELD

    def permission_denied(self, request, **kwargs):
        if (
                settings.HIDE_USERS
                and request.user.is_authenticated
                and self.action in ["update", "partial_update", "list", "retrieve"]
        ):
            raise NotFound()
        super().permission_denied(request, **kwargs)

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()
        if settings.HIDE_USERS and self.action == "list" and not user.is_staff:
            queryset = queryset.filter(pk=user.pk)
        return queryset

    def get_permissions(self):
        if self.action == "create":
            self.permission_classes = settings.PERMISSIONS.user_create
        # elif self.action == "activation":
        #     self.permission_classes = settings.PERMISSIONS.activation
        # elif self.action == "resend_activation":
        #     self.permission_classes = settings.PERMISSIONS.password_reset
        # elif self.action == "list":
        #     self.permission_classes = settings.PERMISSIONS.user_list
        # elif self.action == "reset_password":
        #     self.permission_classes = settings.PERMISSIONS.password_reset
        # elif self.action == "reset_password_confirm":
        #     self.permission_classes = settings.PERMISSIONS.password_reset_confirm
        # elif self.action == "set_password":
        #     self.permission_classes = settings.PERMISSIONS.set_password
        # elif self.action == "set_username":
        #     self.permission_classes = settings.PERMISSIONS.set_username
        # elif self.action == "reset_username":
        #     self.permission_classes = settings.PERMISSIONS.username_reset
        # elif self.action == "reset_username_confirm":
        #     self.permission_classes = settings.PERMISSIONS.username_reset_confirm
        elif self.action == "destroy" or (
                self.action == "me" and self.request and self.request.method == "DELETE"
        ):
            self.permission_classes = settings.PERMISSIONS.user_delete
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action == "create":
            return ProfessorCreateSerializer
        elif self.action == "destroy" or (
                self.action == "me" and self.request and self.request.method == "DELETE"
        ):
            return settings.SERIALIZERS.user_delete
        # elif self.action == "activation":
        #     return settings.SERIALIZERS.activation
        # elif self.action == "resend_activation":
        #     return settings.SERIALIZERS.password_reset
        # elif self.action == "reset_password":
        #     return settings.SERIALIZERS.password_reset
        # elif self.action == "reset_password_confirm":
        #     if settings.PASSWORD_RESET_CONFIRM_RETYPE:
        #         return settings.SERIALIZERS.password_reset_confirm_retype
        #     return settings.SERIALIZERS.password_reset_confirm
        # elif self.action == "set_password":
        #     if settings.SET_PASSWORD_RETYPE:
        #         return settings.SERIALIZERS.set_password_retype
        #     return settings.SERIALIZERS.set_password
        # elif self.action == "set_username":
        #     if settings.SET_USERNAME_RETYPE:
        #         return settings.SERIALIZERS.set_username_retype
        #     return settings.SERIALIZERS.set_username
        # elif self.action == "reset_username":
        #     return settings.SERIALIZERS.username_reset
        # elif self.action == "reset_username_confirm":
        #     if settings.USERNAME_RESET_CONFIRM_RETYPE:
        #         return settings.SERIALIZERS.username_reset_confirm_retype
        #     return settings.SERIALIZERS.username_reset_confirm
        elif self.action == "me":
            return settings.SERIALIZERS.current_user

        return self.serializer_class

    def get_instance(self):
        return self.request.user

    def perform_create(self, serializer, *args, **kwargs):
        user = serializer.save(*args, **kwargs)
        signals.user_registered.send(
            sender=self.__class__, user=user, request=self.request
        )

        # context = {"user": user}
        # to = [get_user_email(user)]
        # if settings.SEND_ACTIVATION_EMAIL:
        #     settings.EMAIL.activation(self.request, context).send(to)
        # elif settings.SEND_CONFIRMATION_EMAIL:
        #     settings.EMAIL.confirmation(self.request, context).send(to)

    def perform_update(self, serializer, *args, **kwargs):
        super().perform_update(serializer)
        user = serializer.instance
        signals.user_updated.send(
            sender=self.__class__, user=user, request=self.request
        )

        # if settings.SEND_ACTIVATION_EMAIL and not user.is_active:
        #     context = {"user": user}
        #     to = [get_user_email(user)]
        #     settings.EMAIL.activation(self.request, context).send(to)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)

        if instance == request.user:
            utils.logout_user(self.request)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(["get", "put", "patch", "delete"], detail=False)
    def me(self, request, *args, **kwargs):
        self.get_object = self.get_instance
        if request.method == "GET":
            return self.retrieve(request, *args, **kwargs)
        elif request.method == "PUT":
            return self.update(request, *args, **kwargs)
        elif request.method == "PATCH":
            return self.partial_update(request, *args, **kwargs)
        elif request.method == "DELETE":
            return self.destroy(request, *args, **kwargs)


class StudentViewSet(ModelViewSet):
    serializer_class = StudentCreateSerializer
    queryset = Student.objects.all()
    permission_classes = settings.PERMISSIONS.user
    token_generator = default_token_generator
    lookup_field = settings.USER_ID_FIELD

    def permission_denied(self, request, **kwargs):
        if (
                settings.HIDE_USERS
                and request.user.is_authenticated
                and self.action in ["update", "partial_update", "list", "retrieve"]
        ):
            raise NotFound()
        super().permission_denied(request, **kwargs)

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()
        if settings.HIDE_USERS and self.action == "list" and not user.is_staff:
            queryset = queryset.filter(pk=user.pk)
        return queryset

    def get_permissions(self):
        if self.action == "create":
            self.permission_classes = settings.PERMISSIONS.user_create
        # elif self.action == "activation":
        #     self.permission_classes = settings.PERMISSIONS.activation
        # elif self.action == "resend_activation":
        #     self.permission_classes = settings.PERMISSIONS.password_reset
        # elif self.action == "list":
        #     self.permission_classes = settings.PERMISSIONS.user_list
        # elif self.action == "reset_password":
        #     self.permission_classes = settings.PERMISSIONS.password_reset
        # elif self.action == "reset_password_confirm":
        #     self.permission_classes = settings.PERMISSIONS.password_reset_confirm
        # elif self.action == "set_password":
        #     self.permission_classes = settings.PERMISSIONS.set_password
        # elif self.action == "set_username":
        #     self.permission_classes = settings.PERMISSIONS.set_username
        # elif self.action == "reset_username":
        #     self.permission_classes = settings.PERMISSIONS.username_reset
        # elif self.action == "reset_username_confirm":
        #     self.permission_classes = settings.PERMISSIONS.username_reset_confirm
        elif self.action == "destroy" or (
                self.action == "me" and self.request and self.request.method == "DELETE"
        ):
            self.permission_classes = settings.PERMISSIONS.user_delete
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action == "create":
            return StudentCreateSerializer
        elif self.action == "destroy" or (
                self.action == "me" and self.request and self.request.method == "DELETE"
        ):
            return settings.SERIALIZERS.user_delete
        # elif self.action == "activation":
        #     return settings.SERIALIZERS.activation
        # elif self.action == "resend_activation":
        #     return settings.SERIALIZERS.password_reset
        # elif self.action == "reset_password":
        #     return settings.SERIALIZERS.password_reset
        # elif self.action == "reset_password_confirm":
        #     if settings.PASSWORD_RESET_CONFIRM_RETYPE:
        #         return settings.SERIALIZERS.password_reset_confirm_retype
        #     return settings.SERIALIZERS.password_reset_confirm
        # elif self.action == "set_password":
        #     if settings.SET_PASSWORD_RETYPE:
        #         return settings.SERIALIZERS.set_password_retype
        #     return settings.SERIALIZERS.set_password
        # elif self.action == "set_username":
        #     if settings.SET_USERNAME_RETYPE:
        #         return settings.SERIALIZERS.set_username_retype
        #     return settings.SERIALIZERS.set_username
        # elif self.action == "reset_username":
        #     return settings.SERIALIZERS.username_reset
        # elif self.action == "reset_username_confirm":
        #     if settings.USERNAME_RESET_CONFIRM_RETYPE:
        #         return settings.SERIALIZERS.username_reset_confirm_retype
        #     return settings.SERIALIZERS.username_reset_confirm
        elif self.action == "me":
            return settings.SERIALIZERS.current_user

        return self.serializer_class

    def get_instance(self):
        return self.request.user

    def perform_create(self, serializer, *args, **kwargs):
        user = serializer.save(*args, **kwargs)
        signals.user_registered.send(
            sender=self.__class__, user=user, request=self.request
        )

        # context = {"user": user}
        # to = [get_user_email(user)]
        # if settings.SEND_ACTIVATION_EMAIL:
        #     settings.EMAIL.activation(self.request, context).send(to)
        # elif settings.SEND_CONFIRMATION_EMAIL:
        #     settings.EMAIL.confirmation(self.request, context).send(to)

    def perform_update(self, serializer, *args, **kwargs):
        super().perform_update(serializer)
        user = serializer.instance
        signals.user_updated.send(
            sender=self.__class__, user=user, request=self.request
        )

        # if settings.SEND_ACTIVATION_EMAIL and not user.is_active:
        #     context = {"user": user}
        #     to = [get_user_email(user)]
        #     settings.EMAIL.activation(self.request, context).send(to)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)

        if instance == request.user:
            utils.logout_user(self.request)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(["get", "put", "patch", "delete"], detail=False)
    def me(self, request, *args, **kwargs):
        self.get_object = self.get_instance
        if request.method == "GET":
            return self.retrieve(request, *args, **kwargs)
        elif request.method == "PUT":
            return self.update(request, *args, **kwargs)
        elif request.method == "PATCH":
            return self.partial_update(request, *args, **kwargs)
        elif request.method == "DELETE":
            return self.destroy(request, *args, **kwargs)
