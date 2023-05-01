from djoser.serializers import UserCreateSerializer
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from django.core.exceptions import ObjectDoesNotExist

from api.models import User, Student
from api.models import Professor
from api.models import CourseGroup
from phonenumber_field.serializerfields import PhoneNumberField
from datetime import datetime


class StudentSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class ProfessorSerializer(ModelSerializer):
    class Meta:
        model = Professor
        fields = '__all__'


class CourseGroupSerializer(ModelSerializer):
    class Meta:
        model = CourseGroup
        fields = '__all__'


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


class StudentCreateSerializer(UserCreateSerializer):
    username = serializers.CharField(max_length=50, source='user.username')
    password = serializers.CharField(source='user.password', write_only=True)
    first_name = serializers.CharField(max_length=20, source='user.first_name')
    second_name = serializers.CharField(max_length=20, source='user.second_name')
    patronymic = serializers.CharField(max_length=20, source='user.patronymic')
    email = serializers.CharField(source='user.email')
    phone = PhoneNumberField(source='user.phone')
    year_of_enrollment = serializers.CharField(max_length=4)
    record_book_number = serializers.CharField(max_length=20)
    course_group_id = serializers.CharField()

    class Meta:
        model = Student
        fields = ('username',
                  'password',
                  'first_name',
                  'second_name',
                  'patronymic',
                  'email',
                  'phone',
                  'year_of_enrollment',
                  'record_book_number',
                  'course_group_id'
                  )

    def validate(self, attrs):

        year_of_enrollment = attrs.get("year_of_enrollment")
        record_book_number = attrs.get("record_book_number")

        try:
            validate_year_of_enrollment(year_of_enrollment)
        except serializers.ValidationError:
            raise serializers.ValidationError("Недопустимое значение года поступления")

        try:
            validate_record_book_number(record_book_number)
        except serializers.ValidationError:
            raise serializers.ValidationError("Недопустимое значение номера студенческого билета")

        return attrs

    def create(self, validated_data):

        try:
            course_group = CourseGroup.objects.get(pk=validated_data['course_group_id'])
        except ObjectDoesNotExist:
            raise serializers.ValidationError("Недопустимое значение course_group_id")
        year_of_enrollment = validated_data['year_of_enrollment']
        record_book_number = validated_data['record_book_number']

        user = User.objects.create(username=validated_data['user']['username'],
                                   first_name=validated_data['user']['first_name'],
                                   second_name=validated_data['user']['second_name'],
                                   patronymic=validated_data['user']['patronymic'],
                                   email=validated_data['user']['email'],
                                   phone=validated_data['user']['phone'])
        user.set_password(validated_data['user']['password'])
        user.save()

        student = Student.objects.create(user=user,
                                         year_of_enrollment=year_of_enrollment,
                                         record_book_number=record_book_number,
                                         course_group=course_group)
        return student
