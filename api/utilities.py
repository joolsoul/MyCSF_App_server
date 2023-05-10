import json
import os

ROOT_PATH = 'C:/Users/Ivan/PycharmProjects/MyCSF_App_server/media/schedules'


def get_professor_schedule(professor=None):
    # identification = 'Зенин К.В.'
    identification = professor.user.second_name + ' ' + professor.user.first_name[0] + '.' + professor.user.patronymic[0] + '.'

    schedule_dict = _create_empty_schedule_dict()

    for file in os.listdir(ROOT_PATH):
        filename = os.fsdecode(file)
        if filename.endswith(".json"):
            current_schedule = json.load(open(ROOT_PATH + '/' + filename, encoding='utf-8', mode="r", ))

            for day, v in current_schedule['numerator'].items():
                for couple in v:
                    if len(couple) != 0 and couple['professor'] == identification:
                        schedule_dict['numerator'][day].append(_create_couple_dict(
                            couple['timeFrom'],
                            couple['timeTo'],
                            couple['subjectName'],
                            couple['classroom']
                        ))

            continue
        else:
            continue

    # with open(ROOT_PATH + '/out.json', encoding='utf-8', mode="w", ) as uu:
    #     json.dump(schedule_dict, uu)

    return schedule_dict


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


def _create_couple_dict(time_from, time_to, subject_name, classroom):
    return {
        'timeFrom': time_from,
        'timeTo': time_to,
        'subjectName': subject_name,
        'classroom': classroom
    }


if __name__ == '__main__':
    get_professor_schedule()
