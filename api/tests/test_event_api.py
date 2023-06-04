from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from rest_framework.utils import json

from api.models import Schedule, User, Event


class EventApiTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        Event.objects.create(title='Аттестация №3 по ИСиС', description='Аттестация №3 по теме: IPv4, IPv6',
                             e_type='a', event_start_datetime='2023-06-03T13:00:00+03:00',
                             event_end_datetime='2023-06-03T13:10:00+03:00', is_full_day=False)

        Event.objects.create(title='День программиста', description='В России 23 сентября отмечается День программиста',
                             e_type='i', event_start_datetime='2023-09-23T12:00:00+03:00',
                             event_end_datetime='2023-09-23T15:00:00+03:00', is_full_day=True)

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

    def test_get_all_events(self):
        endpoint = '/api/event/'
        response = self.client.get(endpoint)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_valid_event(self):
        token = self.response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        endpoint = '/api/event/'
        data = json.dumps(
            {
                'title': 'День открытых дверей на ФКН',
                'description': 'Факультет компьютерных наук приглашает абитуриентов на День открытых дверей!',
                'event_start_datetime': '2023-04-23 10:00:00 +00:00',
                'event_end_datetime': '2023-04-23 13:00:00 +00:00',
                'is_full_day': False,
                'e_type': 'i'
            }
        )
        response = self.client.post(endpoint, data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.test_user.is_staff=True
        self.test_user.save()
        response = self.client.post(endpoint, data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_get_event_detail(self):
        endpoint = '/api/event/1/'
        response = self.client.get(endpoint)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('a', response.data['e_type'])

    def test_partial_update_event(self):
        endpoint = '/api/event/1/'
        response = self.client.get(endpoint)
        self.assertEqual(response.data['title'], 'Аттестация №3 по ИСиС')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.patch(
            endpoint,
            {
                'title': 'Итоговая аттестация по ИСиC'
            }
        )
        self.assertEqual(response.data['title'], 'Итоговая аттестация по ИСиC')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_event(self):
        endpoint = '/api/event/1/'
        response = self.client.get(endpoint)
        self.assertEqual(response.data['title'], 'Аттестация №3 по ИСиС')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.put(
            endpoint,
            {
                'title': 'День рождения ректора!',
                'description': "Декан ФКН празднует юбилей!",
                'event_start_datetime': '2023-03-01 00:00:00 +00:00',
                'event_end_datetime': '2023-03-02 00:00:00 +00:00',
                'is_full_day': True,
                'e_type': 'i'
            }
        )
        self.assertEqual(response.data['title'], 'День рождения ректора!')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_event(self):
        token = self.response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        endpoint = '/api/event/1/'
        response = self.client.get(endpoint)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.delete(endpoint)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.test_user.is_staff = True
        self.test_user.save()
        response = self.client.delete(endpoint)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
