import json
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from api.models import User, Professor


class ProfessorAPITest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.first_user = User.objects.create_user(username='first_user', email='first_user@gmail.com',
                                                  password='pswSla3d029S')
        self.first_user.save()
        self.professor = Professor.objects.create(department='Mathematical', user_id=self.first_user.pk)

        self.endpoint = '/api/auth/jwt/create/'
        self.response = self.client.post(
            self.endpoint,
            {
                'username': 'first_user',
                'password': 'pswSla3d029S'
            },
            format='json'
        )
        self.assertEqual(self.response.status_code, status.HTTP_200_OK)

        self.second_user = User.objects.create_user(username='second_user', email='second_user@gmail.com',
                                               password='kd203sdlA')
        self.second_user.save()
        Professor.objects.create(department='Chemical', user_id=self.second_user.pk)

        self.url = '/api/auth/jwt/create/'
        self.resp = self.client.post(
            self.url,
            {
                'username': 'second_user',
                'password': 'kd203sdlA'
            },
            format='json'
        )
        self.assertEqual(self.resp.status_code, status.HTTP_200_OK)

    def test_get_professors_list(self):
        self.admin = User.objects.create_user(username='admin', password='admin', email='admin@gmail.com')
        self.client.force_authenticate(user=self.admin)

        endpoint = '/api/auth/users/professors/'
        response = self.client.get(endpoint)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])

        self.admin.is_staff = True
        response = self.client.get(endpoint)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEquals(response.data, [])

    def test_create_valid_professor(self):
        endpoint = '/api/auth/users/professors/'
        response = self.client.post(
            endpoint,
            data=json.dumps(
                {
                    'user':
                        {
                            'username': 'valerooon',
                            'password': 'dSfd452pk',
                            'first_name': 'Валерий',
                            'second_name': 'Горев',
                            'patronymic': 'Анатольевич',
                            'email': 'gorev@gmail.com',
                            'phone': '+79009674893'
                        },
                    'department': 'Physical'
                }
            ),
            content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_get_info_about_yourself_by_auth_professor(self):
        token = self.response.data['access']
        endpoint = '/api/auth/users/professors/me/'
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.get(
            endpoint,
            data={
                'format': 'json'
            }
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_info_about_other_professor(self):
        token = self.response.data['access']
        endpoint = '/api/auth/users/professors/2/'
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.get(
            endpoint,
            data={
                'format': 'json'
            }
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)



