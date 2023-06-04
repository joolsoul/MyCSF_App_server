import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django

django.setup()

import datetime
import json

from django.conf import settings
from rest_framework.exceptions import NotFound

from api.models import Schedule

ROOT_PATH = os.path.join(settings.MEDIA_ROOT, 'schedules')


def get_user_schedule(user, user_role, week=None, day=None):
    file = None
    if user_role == 'professor':
        file = get_professor_schedule(user)
    if user_role == 'student':
        file = get_student_schedule(user)

    if week is not None:
        if week == 'n':
            return file['numerator']
        if week == 'd':
            return file['denominator']
        if week == 'a':
            return file
    if day is not None:
        parse_date = datetime.datetime.strptime(day, "%d-%m-%Y").date()
        week_number = parse_date.isocalendar().week
        weekday = parse_date.weekday()

        week_schedule = file

        if week_number % 2 == 0:
            week_schedule = file['denominator']
        else:
            week_schedule = file['numerator']

        if weekday == 0:
            return week_schedule['monday']
        if weekday == 1:
            return week_schedule['tuesday']
        if weekday == 2:
            return week_schedule['wednesday']
        if weekday == 3:
            return week_schedule['thursday']
        if weekday == 4:
            return week_schedule['friday']
        if weekday == 5:
            return week_schedule['saturday']
        if weekday == 6:
            return None

    return file


def get_student_schedule(student):
    try:
        schedule = Schedule.objects.get(course_group_id=student.course_group)
        file = json.load(schedule.schedule_file)
        return file
    except Exception:
        raise NotFound('course group not found')


def get_professor_schedule(professor):
    identification = professor.user.second_name + ' ' + professor.user.first_name[0] + '.' + professor.user.patronymic[
        0] + '.'

    schedule_dict = _create_empty_schedule_dict()

    for file in os.listdir(ROOT_PATH):
        filename = os.fsdecode(file)
        if filename.endswith(".json"):
            current_schedule = json.load(open(ROOT_PATH + '/' + filename, encoding='utf-8', mode="r", ))
        else:
            continue

        for week in current_schedule.keys():
            for day, v in current_schedule[week].items():
                for couple in v:
                    if len(couple) != 0 and couple['professor'] == identification \
                            and _check_uniq_couple(schedule_dict[week][day], couple):
                        schedule_dict[week][day].append(_create_couple_dict(
                            couple['timeFrom'],
                            couple['timeTo'],
                            couple['subjectName'],
                            couple['classroom'],
                            couple['professor']
                        ))
                _sort_couples(schedule_dict[week][day])

            continue
        else:
            continue

    # with open(ROOT_PATH + '/out.json', encoding='utf-8', mode="w", ) as uu:
    #     json.dump(schedule_dict, uu)

    return schedule_dict


def _sort_couples(couples: list):
    couples.sort(key=lambda couple: datetime.datetime.strptime(couple['timeFrom'], '%H:%M'))


def _create_empty_schedule_dict():
    return {
        'numerator': {
            'monday': list(),
            'tuesday': list(),
            'wednesday': list(),
            'thursday': list(),
            'friday': list(),
            'saturday': list()
        },
        'denominator': {
            'monday': list(),
            'tuesday': list(),
            'wednesday': list(),
            'thursday': list(),
            'friday': list(),
            'saturday': list()
        }
    }


def _create_couple_dict(time_from, time_to, subject_name, classroom, professor):
    return {
        'timeFrom': time_from,
        'timeTo': time_to,
        'subjectName': subject_name,
        'classroom': classroom,
        'professor': professor
    }


def _check_uniq_couple(day: list, couple):
    for curr_couple in day:
        if curr_couple['timeFrom'] == couple['timeFrom'] \
                and curr_couple['timeTo'] == couple['timeTo'] \
                and curr_couple['subjectName'] == couple['subjectName'] \
                and curr_couple['classroom'] == couple['classroom']:
            return False
    return True

# if __name__ == "__main__":
#     file = get_professor_schedule()
#     print()
