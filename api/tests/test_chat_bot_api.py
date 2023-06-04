from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from api.models import User


class PublicationApiTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.test_user = User.objects.create_user(username='stepkin', email='stepkin@gmail.com',
                                                  password='kd203sdlA', first_name='Андрей', second_name='Степанов',
                                                  patronymic='Алексеевич', phone='+79009754936',
                                                  is_staff=True)
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

    def test_get_answer_to_question(self):
        endpoint = '/api/chatBot/getAnswer'
        response = self.client.post(
            endpoint,
            {
                'text': 'Привет, как дела?'
            },
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        token = self.response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.post(
            endpoint,
            {
                'text': 'Привет, как дела?'
            },
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
