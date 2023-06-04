import os

import openai

openai.api_key = os.getenv('OPENAI_API_KEY')


def get_answer(text):
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=text,
        temperature=0.8,
        max_tokens=700,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0)

    return response['choices'][0]['text']


# if __name__ == '__main__':
#     print(get_answer("Привет, как дела?"))
