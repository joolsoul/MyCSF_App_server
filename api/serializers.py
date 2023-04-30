from djoser.serializers import UserCreateSerializer
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from api.models import User, Student
from api.models import Professor
from api.models import CourseGroup
from phonenumber_field.serializerfields import PhoneNumberField


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
    username = serializers.CharField(max_length=50, source='user.username')
    password = serializers.CharField(source='user.password', write_only=True)
    first_name = serializers.CharField(max_length=20, source='user.first_name')
    second_name = serializers.CharField(max_length=20, source='user.second_name')
    patronymic = serializers.CharField(max_length=20, source='user.patronymic')
    email = serializers.CharField(source='user.email')
    phone = PhoneNumberField(source='user.phone')
    year_of_enrollment = serializers.CharField(max_length=4)
    record_book_number = serializers.CharField(max_length=20)

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
                  'record_book_number'
                  )

    def validate(self, attrs):
        return attrs

    def create(self, validated_data):
        user = User.objects.create(username=validated_data['user']['username'],
                                   first_name=validated_data['user']['first_name'],
                                   second_name=validated_data['user']['second_name'],
                                   patronymic=validated_data['user']['patronymic'],
                                   email=validated_data['user']['email'],
                                   phone=validated_data['user']['phone'])
        user.set_password(validated_data['user']['password'])
        user.save()
        # TODO: validate fields
        year_of_enrollment = validated_data['year_of_enrollment']
        record_book_number = validated_data['record_book_number']

        student = Student.objects.create(user=user,
                                         year_of_enrollment=year_of_enrollment,
                                         record_book_number=record_book_number)
        return student
