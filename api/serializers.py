from djoser.serializers import UserCreateSerializer
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from api.models import User, Student, Schedule
from api.models import Professor
from api.models import CourseGroup
from rest_framework.exceptions import ParseError
from phonenumber_field.serializerfields import PhoneNumberField

from api.validators import validate_year_of_enrollment, validate_record_book_number, schedule_file_validate


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


class ScheduleSerializer(ModelSerializer):
    class Meta:
        model = Schedule
        fields = '__all__'

    def validate(self, attrs):
        schedule_file = attrs.get("schedule_file")

        try:
            schedule_file_validate(schedule_file)
        except ValueError as error:
            raise ParseError(detail=error.message)

        return attrs


class MyUserCreateSerializer(UserCreateSerializer):
    username = serializers.CharField(max_length=50)
    password = serializers.CharField(write_only=True)
    first_name = serializers.CharField(max_length=20)
    second_name = serializers.CharField(max_length=20)
    patronymic = serializers.CharField(max_length=20)
    email = serializers.CharField()
    phone = PhoneNumberField()

    class Meta:
        model = User
        fields = ('username',
                  'password',
                  'first_name',
                  'second_name',
                  'patronymic',
                  'email',
                  'phone')

    #     teacher/student - user-role

    def create(self, validated_data):
        user = User.objects.create(username=validated_data['username'],
                                   first_name=validated_data['first_name'],
                                   second_name=validated_data['second_name'],
                                   patronymic=validated_data['patronymic'],
                                   email=validated_data['email'],
                                   phone=validated_data['phone'])
        user.set_password(validated_data['password'])
        user.save()
        return user


class ProfessorCreateSerializer(ModelSerializer):
    user = MyUserCreateSerializer(required=True)
    department = serializers.CharField(max_length=50)

    class Meta:
        model = Professor
        fields = ('user',
                  'department')

    def create(self, validated_data):
        department = validated_data['department']
        user_data = validated_data.pop('user')
        user_serializer = MyUserCreateSerializer(data=user_data)
        user_serializer.is_valid(raise_exception=True)
        user = user_serializer.save()

        professor = Professor.objects.create(user=user,
                                             department=department)
        return professor


class StudentCreateSerializer(ModelSerializer):
    user = MyUserCreateSerializer(required=True)
    year_of_enrollment = serializers.CharField(max_length=4)
    record_book_number = serializers.CharField(max_length=20)
    course_group_id = serializers.IntegerField()

    class Meta:
        model = Student
        fields = ('user',
                  'year_of_enrollment',
                  'record_book_number',
                  'course_group_id')

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
        except Exception:
            raise serializers.ValidationError("Недопустимое значение course_group_id")
        year_of_enrollment = validated_data['year_of_enrollment']
        record_book_number = validated_data['record_book_number']

        user_data = validated_data.pop('user')
        user_serializer = MyUserCreateSerializer(data=user_data)
        user_serializer.is_valid(raise_exception=True)
        user = user_serializer.save()

        student = Student.objects.create(user=user,
                                         year_of_enrollment=year_of_enrollment,
                                         record_book_number=record_book_number,
                                         course_group=course_group)
        return student
