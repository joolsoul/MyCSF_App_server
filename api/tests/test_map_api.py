from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from api.models import Schedule, CourseGroup, User, Professor, Student, Map


class MapApiTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        courseGroup_3_5 = CourseGroup.objects.create(course_number=3, group_number='5', higher_education_level='b')
        Schedule.objects.create(schedule_file='schedules/3_5.2_b.json', course_group_id=courseGroup_3_5.pk)
        self.student = User.objects.create_user(username='vitalik', email='vitalik@gmail.com',
                                                password='pkla24pas', first_name='Виталий',
                                                second_name='Панов', patronymic='Валерьевич', phone='+79009272093')
        Student.objects.create(year_of_enrollment='2', record_book_number='1629071',
                               course_group_id=courseGroup_3_5.pk, user_id=self.student.pk)
        self.client.login(username=self.student.username, password='pkla24pas')
        self.endpoint = '/api/auth/jwt/create/'
        self.response = self.client.post(
            self.endpoint,
            {
                'username': 'vitalik',
                'password': 'pkla24pas'
            },
            format='json'
        )
        self.assertEqual(self.response.status_code, status.HTTP_200_OK)

        Map.objects.create(building="1a", building_level="2", map_file='maps/ex1a_2.png')
        Map.objects.create(building="1a", building_level="3", map_file='maps/ex1a_3.png')
        Map.objects.create(building="1a", building_level="4", map_file='maps/ex1a_4.png')
        Map.objects.create(building="1b", building_level="3", map_file='maps/ex1b_3.png')
        Map.objects.create(building="1b", building_level="5", map_file='maps/ex1a_5.png')
        Map.objects.create(building="m", building_level="1", map_file='maps/m_0.png')

    def test_get_all_maps_list(self):
        endpoint = '/api/map/'
        response = self.client.get(endpoint)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_maps_list_of_certain_building(self):
        endpoint = '/api/map/?building=1a'
        response = self.client.get(endpoint)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_buildings_list(self):
        endpoint = '/api/map/choices/'
        response = self.client.get(endpoint)
        expected_data = {
            'm': 'main building',
            'ex1a': 'extension building 1A',
            'ex1b': 'extension building 1B'
        }
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(expected_data, response.data)

    def test_get_map_detail(self):
        endpoint = '/api/map/2/'
        response = self.client.get(endpoint)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('map_file', response.data)

        file_link = response.data['map_file']
        self.assertTrue(file_link.startswith('http://testserver/media/'))
        self.assertIn('maps/ex1a_3.png', file_link)

    def test_delete_map(self):
        admin = User.objects.create_user(username='admin', password='root', email='test@gmail.com', is_staff=True)
        self.client.login(username=admin.username, password='root')
        endpoint = '/api/map/2/'
        response = self.client.get(endpoint)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('map_file', response.data)

        response = self.client.delete(endpoint)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        response = self.client.get(endpoint)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)