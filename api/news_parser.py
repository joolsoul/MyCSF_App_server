import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django
django.setup()
import datetime
import requests

from api.models import Publication
from api.serializers import PublicationSerializer
from dotenv import load_dotenv

load_dotenv()


def get_news():
    response = requests.get('https://api.vk.com/method/wall.get',
                            params={'access_token': os.getenv('TOKEN_USER'),
                                    'v': os.getenv('VERSION'),
                                    'domain': os.getenv('DOMAIN'),
                                    'count': os.getenv('NEWS_COUNT'),
                                    'filter': str('owner')})

    data = response.json()['response']['items']

    for post in sorted(data, key=lambda item: item['date']):
        try:
            validated_data = {'image': None,
                              'body_text': '',
                              'title': '',
                              'publication_datetime': datetime.datetime.fromtimestamp(post['date'])}

            if 'copy_history' in post:
                parent_post = post['copy_history'][0]
                if parent_post['text'] is None or len(parent_post['text']) == 0:
                    continue
                validated_data['body_text'] = parent_post['text'][:2000]
                validated_data['image'] = get_photo(parent_post['attachments'])

            else:
                if post['text'] is None or len(post['text']) == 0:
                    continue
                validated_data['body_text'] = post['text'][:2000]
                validated_data['image'] = get_photo(post['attachments'])

            validated_data['title'] = " ".join(validated_data['body_text'].split()[:4])

            latest_publication = None
            if Publication.objects.count() != 0:
                latest_publication = Publication.objects.latest('publication_datetime')

            if latest_publication is None or validated_data['publication_datetime'].timestamp() > \
                    latest_publication.publication_datetime.timestamp():
                PublicationSerializer().create(validated_data)

        except Exception as e:
            print(f"CRON ERR: {e}")


def get_photo(attachments: list):
    photo = []
    for attachment in attachments:
        if attachment['type'] == 'photo':
            for size in attachment['photo']['sizes']:
                if size['type'] == 'w':
                    photo.append(size['url'])

    if len(photo) != 0:
        return photo[0]


# if __name__ == '__main__':
#     get_news()
