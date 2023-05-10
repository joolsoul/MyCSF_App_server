from django.urls import path, include
from rest_framework import routers

from api.views import CourseGroupApiList, UserShortInfoViewSet
from api.views import ProfessorApiList
from api.views import StudentApiList, StudentViewSet, ProfessorViewSet, ScheduleApiList, ScheduleApi

router = routers.SimpleRouter()
router.register('auth/users/students', StudentViewSet)
router.register('auth/users/professors', ProfessorViewSet)
router.register('auth/users/shortinfo', UserShortInfoViewSet)

urlpatterns = [
    path('student/', StudentApiList.as_view()),
    path('professor/', ProfessorApiList.as_view()),
    path('courseGroup/', CourseGroupApiList.as_view()),
    path('schedule/', ScheduleApiList.as_view()),
    path('schedule/<int:pk>/', ScheduleApi.as_view()),
    path('auth/', include('djoser.urls.jwt')),
    # path('auth/users/shortinfo', UserShortInfoView.as_view())
]

urlpatterns += router.urls
