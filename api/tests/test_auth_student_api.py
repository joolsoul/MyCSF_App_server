import json

from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from api.models import User, Student, CourseGroup


class StudentAPITest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.courseGroup_3_5 = CourseGroup.objects.create(course_number=3, group_number='5', higher_education_level='b')
        self.student = User.objects.create_user(username='iliyich', email='ilyuha@gmail.com',
                                                password='ad85Flsj', first_name='Илья',
                                                second_name='Петухов', patronymic='Сергеевич', phone='+79007424593')
        Student.objects.create(year_of_enrollment='2020', record_book_number='16200742',
                               course_group_id=self.courseGroup_3_5.pk, user_id=self.student.pk)

        self.endpoint = '/api/auth/jwt/create/'
        self.response = self.client.post(
            self.endpoint,
            {
                'username': 'iliyich',
                'password': 'ad85Flsj'
            },
            format='json'
        )
        self.assertEqual(self.response.status_code, status.HTTP_200_OK)

        self.courseGroup_3_4 = CourseGroup.objects.create(course_number=3, group_number='4', higher_education_level='b')
        self.second_student = User.objects.create_user(username='vlaskan', email='vlaskan@gmail.com',
                                                password='93loSFksp', first_name='Антон',
                                                second_name='Сергеев', patronymic='Игоревич', phone='+79080124593')
        Student.objects.create(year_of_enrollment='2', record_book_number='16200191',
                               course_group_id=self.courseGroup_3_4.pk, user_id=self.second_student.pk)

        self.endpoint = '/api/auth/jwt/create/'
        self.resp = self.client.post(
            self.endpoint,
            {
                'username': 'vlaskan',
                'password': '93loSFksp'
            },
            format='json'
        )
        self.assertEqual(self.resp.status_code, status.HTTP_200_OK)

    def test_get_auth_users_list(self):
        # self.admin = User.objects.create_user(username='admin', password='admin', email='admin@gmail.com')
        # self.client.force_authenticate(user=self.admin)
        token = self.response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

        endpoint = '/api/auth/users/students/'
        response = self.client.get(endpoint)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # self.assertEqual(response.data, [])
        print(response.data)

        self.student.is_staff = True
        response = self.client.get(endpoint)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEquals(response.data, [])

    def test_create_valid_student(self):
        endpoint = '/api/auth/users/students/'
        response = self.client.post(
            endpoint,
            data=json.dumps(
                {
                    'user':
                        {
                            'username': 'vyatkin51',
                            'password': 'hs92lsaLKas',
                            'first_name': 'Артём',
                            'second_name': 'Вяткин',
                            'patronymic': 'Викторович',
                            'email': 'vyaatkin@gmail.com',
                            'phone': '+79009674893'
                        },
                    'year_of_enrollment': '2022',
                    'record_book_number': '16200792',
                    'course_group_id': self.courseGroup_3_5.pk
                }
            ),
            content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_get_info_about_yourself_by_auth_user(self):
        token = self.response.data['access']
        endpoint = '/api/auth/users/students/me/'
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.get(
            endpoint,
            data={
                'format': 'json'
            }
        )
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_info_about_other_student(self):
        token = self.response.data['access']
        endpoint = '/api/auth/users/students/2/'
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.get(
            endpoint,
            data={
                'format': 'json'
            }
        )
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
