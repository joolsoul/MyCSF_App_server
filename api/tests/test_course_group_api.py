from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from rest_framework.utils import json
from api.models import CourseGroup, User
from api.serializers import CourseGroupSerializer


class CourseGroupAPITest(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(username='admin', password='root', email='test@gmail.com',
                                             is_superuser=True, is_staff=True, is_active=True, is_verified=True)
        self.admin.save()
        self.client = APIClient()
        self.client.login(username=self.admin.username, password='root')

        CourseGroup.objects.create(course_number=3, group_number='3.1', higher_education_level='b')
        CourseGroup.objects.create(course_number=1, group_number='2', higher_education_level='m')

    def test_get_courseGroup_list(self):
        response = self.client.get(reverse('courseGroup'))
        courseGroups = CourseGroup.objects.all()
        serializer = CourseGroupSerializer(courseGroups, many=True)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_valid_courseGroup(self):
        response = self.client.post(
            reverse('courseGroup'),
            data=json.dumps(
                {
                    'course_number': 1,
                    'group_number': '2',
                    'higher_education_level': 'm'}),
            content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_invalid_courseGroup(self):
        response = self.client.post(
            reverse('courseGroup'),
            data=json.dumps(
                {
                    'course_number': 1,
                    'group_number': '',
                    'higher_education_level': 's'
                }
            ),
            content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)



