from djoser.serializers import UserCreateSerializer
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from api.models import User, Student
from api.models import Professor
from api.models import CourseGroup


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


class StudentCreateSerializer(UserCreateSerializer):
    year_of_enrollment = serializers.CharField(max_length=4, write_only=True)
    record_book_number = serializers.CharField(max_length=20, write_only=True)

    class Meta:
        model = User
        fields = ('username',
                  'password',
                  'first_name',
                  'second_name',
                  'patronymic',
                  'email',
                  'phone',
                  'year_of_enrollment',
                  'record_book_number'
                  )

    def validate(self, attrs):
        # year_of_enrollment = attrs.pop('year_of_enrollment')
        # record_book_number = attrs.pop('record_book_number')
        # print(attrs)
        # return super().validate(attrs)
        return attrs

    def create(self, validated_data):
        user = User.objects.create(username=validated_data['username'],
                                   first_name=validated_data['first_name'],
                                   second_name=validated_data['second_name'],
                                   patronymic=validated_data['patronymic'],
                                   email=validated_data['email'],
                                   phone=validated_data['phone'])
        user.set_password(validated_data['password'])
        # TODO: validate fields
        year_of_enrollment = validated_data['year_of_enrollment']
        record_book_number = validated_data['record_book_number']

        student = Student.objects.create(user=user,
                                         year_of_enrollment=year_of_enrollment,
                                         record_book_number=record_book_number)
        return user

