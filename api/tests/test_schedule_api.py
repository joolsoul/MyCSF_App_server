from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from api.models import Schedule, CourseGroup, User, Professor, Student


class ScheduleApiTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.professor = User.objects.create_user(username='flapson', email='flapson@gmail.com',
                                              password='kd203sdlAsg',
                                              first_name='Кирилл', second_name='Зенин', patronymic='Вячеславович')
        Professor.objects.create(department='Mathematical', user_id=self.professor.pk)
        self.endpoint = '/api/auth/jwt/create/'
        self.response = self.client.post(
            self.endpoint,
            {
                'username': 'flapson',
                'password': 'kd203sdlAsg'
            },
            format='json'
        )
        self.assertEqual(self.response.status_code, status.HTTP_200_OK)

        # courseGroup_3_5 = CourseGroup.objects.create(course_number=3, group_number='5', higher_education_level='b')
        # Schedule.objects.create(schedule_file='schedules/3_5.2_b.json', course_group_id=courseGroup_3_5.pk)
        # self.student = User.objects.create_user(username='andrew', email='maloy@gmail.com',
        #                                         password='pla232piSR', first_name='Андрей',
        #                                         second_name='Иванков', patronymic='Валерьевич', phone='+79009284593')
        # Student.objects.create(year_of_enrollment='2', record_book_number='1629071',
        #                        course_group_id=courseGroup_3_5.pk, user_id=self.student.pk)
        # self.url = '/api/auth/jwt/create/'
        # self.resp = self.client.post(
        #     self.url,
        #     {
        #         'username': 'andrew',
        #         'password': 'pla232piSR'
        #     },
        #     format='json'
        # )
        # self.assertEqual(self.response.status_code, status.HTTP_200_OK)

    def test_get_lessons_list_for_professor(self):
        endpoint = '/api/schedule/1/?w=n'
        response = self.client.get(endpoint)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        token = self.response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.get(endpoint)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(type(response.data), dict)



        data = response.data
        schedule = {
            'monday': data['numerator']['monday'],
            'tuesday': data['numerator']['tuesday'],
            'wednesday': data['numerator']['wednesday'],
            'thursday': data['numerator']['thursday'],
            'friday': data['numerator']['friday'],
            'saturday': data['numerator']['saturday']
        }
        lessonsCountPerWeek = 0
        days = schedule.keys()
        for key in days:
            lessonsCountPerDay = len(schedule[key])
            for i in range(lessonsCountPerDay):
                if len(schedule[key][i]) != 0:
                    lessonsCountPerWeek += 1
        self.assertEqual(lessonsCountPerWeek, 6)

    def test_get_lessons_list_per_week_for_professor(self):
        token = self.response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

        endpoint = '/api/schedule/1/?week=d'
        response = self.client.get(endpoint)
        schedule = response.data
        lessonsCountPerDenominator = 0
        days = schedule.keys()
        for key in days:
            lessonsCountPerDay = len(schedule[key])
            for i in range(lessonsCountPerDay):
                if len(schedule[key][i]) != 0:
                    lessonsCountPerDenominator += 1
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(type(schedule), dict)
        self.assertEqual(lessonsCountPerDenominator, 7)

    def test_get_lessons_list_for_student(self):
        token = self.response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        # self.client.login(username=self.student.username, password='pla232piSR')
        endpoint = '/api/schedule/2/?week=a'
        response = self.client.get(endpoint)
        schedule = response.data
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        days = schedule.keys()
        lessonsCountPerTwoWeek = 0
        for key in days:
            lessonsCountPerDay = len(schedule[key])
            for i in range(lessonsCountPerDay):
                if len(schedule[key][i]) != 0:
                    lessonsCountPerTwoWeek += 1
        self.assertEqual(lessonsCountPerTwoWeek, 7)

    