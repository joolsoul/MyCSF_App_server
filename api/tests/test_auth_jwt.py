from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from rest_framework.utils import json
from api.models import Professor, User


class AuthJwtTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.auth_user = User.objects.create_user(username='sergeyich', email='test_user@gmail.com',
                                                  password='pswRkIsaEhd42')
        self.auth_user.save()
        Professor.objects.create(department='Computer science', user_id=self.auth_user.pk)

        self.endpoint = '/api/auth/jwt/create/'
        self.response = self.client.post(
            self.endpoint,
            {
                'username': 'sergeyich',
                'password': 'pswRkIsaEhd42'
            },
            format='json'
        )
        self.assertEqual(self.response.status_code, status.HTTP_200_OK)

    def test_auth_jwt_create(self):
        self.test_user = User.objects.create_user(username='palych', email='palych@gmail.com',
                                                  password='ks94lsaPF')
        Professor.objects.create(department='Computer science', user_id=self.test_user.pk)

        endpoint = '/api/auth/jwt/create/'
        self.test_user.is_active = False
        self.test_user.save()
        response = self.client.post(
            endpoint,
            {
                'username': 'palych',
                'password': 'ks94lsaPF'
            },
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.test_user.is_active=True
        self.test_user.save()
        response = self.client.post(
            endpoint,
            {
                'username': 'palych',
                'password': 'ks94lsaPF'
            },
            format='json'
        )
        self.assertTrue('refresh' in response.data)
        self.assertTrue('access' in response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_auth_jwt_verify(self):
        endpoint = '/api/auth/jwt/verify/'
        response = self.client.post(
            endpoint,
            {
                'token': self.response.data['access']
            },
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_auth_jwt_refresh(self):
        old_token = self.response.data['access']
        endpoint = '/api/auth/jwt/refresh/'
        response = self.client.post(
            endpoint,
            {
                'refresh': self.response.data['refresh']
            },
            format='json'
        )
        new_token = response.data['access']
        self.assertNotEquals(old_token, new_token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)