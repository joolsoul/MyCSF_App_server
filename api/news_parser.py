from datetime import datetime
import requests

from api.serializers import PublicationCreateSerializer

TOKEN = 'https://oauth.vk.com/blank.html#access_token=vk1.a.AqZZH30Ff8OGP-PQo8hBft1iFwq_h7H-OUAyD5nIQTY1cgp6BmNcurB2w1xX1TXy781Ur1m53AgS2HZdj0H41Fgrcmag48_b_YrjQU_aSJw0MOdyfPQrxnf2bxCeINbxROq8GG4vDbx0sIHXhpN3EsvA7gusq-TepauQ4VZVuvy7e5_Ej7I64LMjbf96cTzKX0QsEE61ZnCVbzTbJqW_Cw&expires_in=0&user_id=216989823'

TOKEN_USER = 'vk1.a.AqZZH30Ff8OGP-PQo8hBft1iFwq_h7H-OUAyD5nIQTY1cgp6BmNcurB2w1xX1TXy781Ur1m53AgS2HZdj0H41Fgrcmag48_b_YrjQU_aSJw0MOdyfPQrxnf2bxCeINbxROq8GG4vDbx0sIHXhpN3EsvA7gusq-TepauQ4VZVuvy7e5_Ej7I64LMjbf96cTzKX0QsEE61ZnCVbzTbJqW_Cw'
VERSION = '5.131'
DOMAIN = 'cs_vsu'


# TODO: Баг с переводом времени из timestamp XD) разница ровно в 3 часа
def get_news():
    response = requests.get('https://api.vk.com/method/wall.get',
                            params={'access_token': TOKEN_USER,
                                    'v': VERSION,
                                    'domain': DOMAIN,
                                    'count': 10,
                                    'filter': str('owner')})

    data = response.json()['response']['items']

    for post in data:
        validated_data = {'photo': [],
                          'body_text': '',
                          'title': '',
                          'publication_datetime': datetime.utcfromtimestamp(post['date']).strftime('%Y-%m-%d %H:%M:%S')}

        if 'copy_history' in post:
            parent_post = post['copy_history'][0]
            validated_data['body_text'] = parent_post['text']
            get_photo(validated_data['photo'], parent_post['attachments'])

        else:
            validated_data['body_text'] = post['text']
            get_photo(validated_data['photo'], post['attachments'])

        validated_data['title'] = validated_data['body_text'][:4]

        PublicationCreateSerializer().create(validated_data)
    print('asds')
    

def get_photo(photo: list, attachments: list):
    for attachment in attachments:
        if attachment['type'] == 'photo':
            for size in attachment['photo']['sizes']:
                if size['type'] == 'w':
                    photo.append(size['url'])

if __name__ == '__main__':
    get_news()
