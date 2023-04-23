from django.contrib import admin
from django.urls import path

from api.views import StudentApiList
from api.views import ProfessorApiList
from api.views import CourseGroupApiList

urlpatterns = [
    path('student/', StudentApiList.as_view()),
    path('professor/', ProfessorApiList.as_view()),
    path('courseGroup/', CourseGroupApiList.as_view())
]
