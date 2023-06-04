from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from rest_framework.utils import json
from api.models import CourseGroup, User
from api.serializers import CourseGroupSerializer


class CourseGroupAPITest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.test_user = User.objects.create_user(username='stepkin', email='stepkin@gmail.com',
                                                  password='kd203sdlA', first_name='Андрей', second_name='Степанов',
                                                  patronymic='Алексеевич', phone='+79009754936',
                                                  is_staff=False)
        self.endpoint = '/api/auth/jwt/create/'
        self.response = self.client.post(
            self.endpoint,
            {
                'username': 'stepkin',
                'password': 'kd203sdlA'
            },
            format='json'
        )
        self.assertEqual(self.response.status_code, status.HTTP_200_OK)
        CourseGroup.objects.create(course_number=3, group_number='3.1', higher_education_level='b')
        CourseGroup.objects.create(course_number=1, group_number='2', higher_education_level='m')

    def test_get_courseGroup_list(self):
        response = self.client.get(reverse('courseGroup'))
        courseGroups = CourseGroup.objects.all()
        serializer = CourseGroupSerializer(courseGroups, many=True)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_valid_courseGroup(self):
        token = self.response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.post(
            reverse('courseGroup'),
            data=json.dumps(
                {
                    'course_number': 1,
                    'group_number': '2',
                    'higher_education_level': 'm'}),
            content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.test_user.is_staff = True
        self.test_user.save()
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
        self.test_user.is_staff = True
        self.test_user.save()
        token = self.response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
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



