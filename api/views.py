import json

from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from djoser import signals, utils
from djoser.conf import settings
from rest_framework import generics, status
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.mixins import RetrieveModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from rest_framework.viewsets import ModelViewSet, GenericViewSet

from api.models import Student, Professor, CourseGroup, Schedule, Map
from api.permissions import AdminOrReadOnlyPermission
from api.serializers import CourseGroupSerializer, MyUserCreateSerializer
from api.serializers import ProfessorSerializer, ScheduleSerializer, MapSerializer
from api.serializers import StudentSerializer, StudentCreateSerializer, ProfessorCreateSerializer
from api.utilities import get_professor_schedule

User = get_user_model()


# Create your views here.

class ScheduleApiList(generics.ListAPIView):
    queryset = Schedule.objects.all()
    serializer_class = ScheduleSerializer


class ScheduleApi(generics.RetrieveAPIView):
    queryset = Schedule.objects.all()
    serializer_class = ScheduleSerializer


class StudentApiList(generics.ListCreateAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer


class ProfessorApiList(generics.ListCreateAPIView):
    queryset = Professor.objects.all()
    serializer_class = ProfessorSerializer


class CourseGroupApiList(generics.ListCreateAPIView):
    queryset = CourseGroup.objects.all()
    serializer_class = CourseGroupSerializer
    permission_classes = [AdminOrReadOnlyPermission]


class MapApiView(ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Map.objects.all()
    serializer_class = MapSerializer

    def get_queryset(self):
        building = self.request.query_params.get('building')
        queryset = Map.objects.filter(building=building)
        return queryset


class UserScheduleViewSet(RetrieveModelMixin, GenericViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Schedule.objects.all()
    serializer_class = ScheduleSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        return Response(instance, status=HTTP_200_OK)

    def get_object(self):
        try:
            user = self.request.user
        except Exception:
            raise NotFound('user not found')
        err_count = 0
        try:
            student = user.student
            course_group = student.course_group

            try:
                schedule = Schedule.objects.get(course_group_id=course_group)
                file = json.load(schedule.schedule_file)
                return file
            except Exception:
                raise NotFound('course group not found')

        except Exception:
            err_count += 1

        try:
            professor = user.professor
            professor_schedule = get_professor_schedule(professor)
            return professor_schedule
        except Exception:
            err_count += 1

        if err_count >= 2:
            raise Exception('user dont load')


# id - ignored
class UserShortInfoViewSet(RetrieveModelMixin, GenericViewSet):
    permission_classes = [IsAuthenticated]
    queryset = User.objects.all()
    serializer_class = MyUserCreateSerializer

    def get_object(self):
        # user = self.request.user
        # student = user.student

        return self.request.user


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

class ProfessorViewSet(ModelViewSet):
    serializer_class = ProfessorCreateSerializer
    queryset = User.objects.all()
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
    queryset = User.objects.all()
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
