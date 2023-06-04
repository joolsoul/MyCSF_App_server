from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from api.models import User, Event, Publication


class PublicationApiTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.event = Event.objects.create(title='День программиста',
                                          description='В России 23 сентября отмечается День программиста',
                                          e_type='i', event_start_datetime='2023-09-23T12:00:00+03:00',
                                          event_end_datetime='2023-09-23T15:00:00+03:00', is_full_day=True)
        self.test_user = User.objects.create_user(username='stepkin', email='stepkin@gmail.com',
                                                  password='kd203sdlA', first_name='Андрей', second_name='Степанов',
                                                  patronymic='Алексеевич', phone='+79009754936',
                                                  is_staff=True)
        self.endpoint = '/api/auth/jwt/create/'
        self.resp = self.client.post(
            self.endpoint,
            {
                'username': 'stepkin',
                'password': 'kd203sdlA'
            },
            format='json'
        )
        self.assertEqual(self.resp.status_code, status.HTTP_200_OK)
        self.client.login(username=self.test_user.username, password='kd203sdlA')

        Publication.objects.create(title='День программиста в России!', body_text='День программи́ста — '
                                                                                  'профессиональный праздник в РФ, отмечаемый в 256-й день года.',
                                   publication_datetime='2023-03-02 00:00:00 +00:00', event_id=self.event.pk)
        Publication.objects.create(title='День карьеры на ФКН!', body_text='29 апреля Факультет компьютерных наук '
                                                                           'приглашает всех студентов IT-специальностей , а также выпускников на день карьеры.',
                                   publication_datetime='2022-04-20 10:00:00 +00:00')
        Publication.objects.create(title='День открытых дверей на ФКН!', body_text='Студенческий совет факультета '
                                                                                   'компьютерных наук ВГУ приглашает вас на встречу, где вы сможете задать все '
                                                                                   'интересующие вас вопросы о поступлении.',
                                   publication_datetime='2022-06-10 12:00:00 +00:00')

    def test_get_all_publications(self):
        endpoint = '/api/publication/'
        response = self.client.get(endpoint)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)

    def test_get_limited_number_of_publications(self):
        endpoint = '/api/publication/?limit=2'
        response = self.client.get(endpoint)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
