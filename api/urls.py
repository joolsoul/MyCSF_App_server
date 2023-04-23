from django.contrib import admin
from django.urls import path
from rest_framework import routers

from api.views import StudentApiList, StudentViewSet
from api.views import ProfessorApiList
from api.views import CourseGroupApiList

router = routers.SimpleRouter()
router.register('auth/users/students', StudentViewSet)

urlpatterns = [
    path('student/', StudentApiList.as_view()),
    path('professor/', ProfessorApiList.as_view()),
    path('courseGroup/', CourseGroupApiList.as_view()),
    # path('auth/users/student', StudentCreateView.as_view())
]

urlpatterns += router.urls