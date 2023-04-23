from rest_framework import generics

from api.models import Student
from api.models import Professor
from api.models import CourseGroup
from api.serializers import StudentSerializer
from api.serializers import ProfessorSerializer
from api.serializers import CourseGroupSerializer


# Create your views here.

class StudentApiList(generics.ListCreateAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer


class ProfessorApiList(generics.ListCreateAPIView):
    queryset = Professor.objects.all()
    serializer_class = ProfessorSerializer


class CourseGroupApiList(generics.ListCreateAPIView):
    queryset = CourseGroup.objects.all()
    serializer_class = CourseGroupSerializer
