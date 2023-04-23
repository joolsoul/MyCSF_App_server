from rest_framework.serializers import ModelSerializer

from api.models import User
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
