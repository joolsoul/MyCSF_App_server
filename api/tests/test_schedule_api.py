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
        self.client.login(username=self.professor.username, password='kd203sdlAsg')

        courseGroup_3_5 = CourseGroup.objects.create(course_number=3, group_number='5', higher_education_level='b')
        Schedule.objects.create(schedule_file='schedules/3_5.2_b.json', course_group_id=courseGroup_3_5.pk)
        self.student = User.objects.create_user(username='andrew', email='maloy@gmail.com',
                                                password='pla232piSR', first_name='Андрей',
                                                second_name='Иванков', patronymic='Валерьевич', phone='+79009284593')
        Student.objects.create(year_of_enrollment='2', record_book_number='1629071',
                               course_group_id=courseGroup_3_5.pk, user_id=self.student.pk)
        self.endpoint = '/api/auth/jwt/create/'
        self.response = self.client.post(
            self.endpoint,
            {
                'username': 'andrew',
                'password': 'pla232piSR'
            },
            format='json'
        )
        self.assertEqual(self.response.status_code, status.HTTP_200_OK)

    def test_get_lessons_list_for_professor(self):
        endpoint = '/api/schedule/1/'
        response = self.client.get(endpoint)
        data = response.data
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(type(response.data), dict)
        schedule = {
            'monday': data['numerator']['monday'] + data['denominator']['monday'],
            'tuesday': data['numerator']['tuesday'] + data['denominator']['tuesday'],
            'wednesday': data['numerator']['wednesday'] + data['denominator']['wednesday'],
            'thursday': data['numerator']['thursday'] + data['denominator']['thursday'],
            'friday': data['numerator']['friday'] + data['denominator']['friday'],
            'saturday': data['numerator']['saturday'] + data['denominator']['saturday']
        }
        days = schedule.keys()
        expectedCount = 0
        for key in days:
            lessonsDict = schedule[key]
            if key == 'monday':
                for i in range(len(lessonsDict)):
                    if schedule[key][i]['subjectName'] == 'Философия':
                        expectedCount += 1
        self.assertEqual(expectedCount, 3)

    def test_get_lessons_list_per_week_for_professor(self):
        endpoint = '/api/schedule/1/?week=n'
        response = self.client.get(endpoint)
        schedule = response.data
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(type(schedule), dict)
        self.assertEqual(len(schedule), 6)

    def test_get_lessons_list_for_student(self):
        self.client.login(username=self.student.username, password='pla232piSR')
        endpoint = '/api/schedule/1/?week=d'
        response = self.client.get(endpoint)
        schedule = response.data
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        days = schedule.keys()
        expectedCount = 0
        for key in days:
            lessonsDict = schedule[key]
            expectedCount += len(lessonsDict)
        self.assertEqual(expectedCount, 7)

    