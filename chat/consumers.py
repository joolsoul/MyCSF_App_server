import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django
django.setup()

import json
from pprint import pprint

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.layers import get_channel_layer
from django.db.models import Q

from chat.models import ChatParticipantsChannel, ChatRoomParticipants, ChatRoom, Messages
from django.contrib.auth import get_user_model

User = get_user_model()


class ChatConsumer(AsyncJsonWebsocketConsumer):

    async def connect(self):
        pprint(self.scope)
        self.user_id = self.scope['url_route']['kwargs']['user_id']

        await self.accept()

        await self.save_user_channel()

    @database_sync_to_async
    def save_user_channel(self):
        self.user = User.objects.get(id=self.user_id)

        ChatParticipantsChannel.objects.create(
            user=self.user,
            channel=self.channel_name
        )

    async def receive_json(self, text_data=None, byte_data=None):
        print(text_data, self.user)
        message = text_data['message']
        self.to_user = text_data['to_user']
        to_user_channel, to_user_id = await self.get_user_channel(self.to_user)
        pprint(message)
        self.group_name = f'{self.user_id}-{self.to_user}'
        message_response = await self.save_message(self.group_name, self.user, message)
        message_response['type'] = 'send.message'

        channel_layer = get_channel_layer()

        await self.channel_layer.group_add(
            self.group_name,
            str(self.channel_name)
        )
        if to_user_channel is not None and to_user_id is not None:
            await self.channel_layer.group_add(
                self.group_name,
                str(to_user_channel)
            )

        await channel_layer.group_send(
            self.group_name, message_response
        )

    @database_sync_to_async
    def save_message(self, room, user, content):
        # try:
        #     ChatRoomParticipants.objects.get_or_create(
        #         Q(room__name=f'{self.user.user_uid}-{self.to_user}') |
        #         Q(room__name=f'{self.to_user}-{self.user.user_uid}'), user=self.user)
        #     ChatRoomParticipants.objects.get_or_create(
        #         Q(room__name=f'{self.user.user_uid}-{self.to_user}') |
        #         Q(room__name=f'{self.to_user}-{self.user.user_uid}'), user=self.to_user)
        # except Exception as e:
        #     print(e)

        try:
            chatroom = ChatRoom.objects.get(Q(name=f'{self.user.id}-{self.to_user}') |
                                            Q(name=f'{self.to_user}-{self.user.id}'))
            chatroom.last_message = content
            chatroom.last_sent_user = self.user
        except Exception as e:
            chatroom = ChatRoom.objects.create(
                name=str(room),
                last_message=content,
                last_sent_user=self.user
            )
        filtered_objects1 = ChatRoomParticipants.objects.filter(Q(room__name=f'{self.user.id}-{self.to_user}') | Q(room__name=f'{self.to_user}-{self.user.id}'), user=self.user)
        filtered_objects2 = ChatRoomParticipants.objects.filter(Q(room__name=f'{self.user.id}-{self.to_user}') | Q(room__name=f'{self.to_user}-{self.user.id}'), user=self.to_user)

        if not filtered_objects1.exists():
            ChatRoomParticipants.objects.create(room=chatroom, user=self.user)

        if not filtered_objects2.exists():
            ChatRoomParticipants.objects.create(room=chatroom, user=User.objects.get(id=self.to_user))

        message = Messages.objects.create(
            room=chatroom, user=self.user, content=content
        )

        message_response = {
            'message_id': message.id,
            'message_room': chatroom.id,
            'message_content': message.content,
            'message_user': str(message.user.id),
            'message_created_at': str(message.created_at),
        }
        print(message_response)
        return message_response

    async def send_message(self, event):
        # from_user = event['from_user']
        # to_user = event['to_user']
        # message = event['message']

        print(event)

        await self.send(text_data=json.dumps(event))

    @database_sync_to_async
    def get_user_channel(self, to_user):
        try:
            send_user_channel = ChatParticipantsChannel.objects.filter(
                user=to_user).latest('id')
            channel_name = send_user_channel
            user_id = send_user_channel.user.id
        except Exception as e:
            channel_name = None
            user_id = None

        return channel_name, user_id

    async def disconnect(self, close_code):
        await self.delete_user_channel()

        await super(ChatConsumer, self).disconnect(close_code)

    @database_sync_to_async
    def delete_user_channel(self):
        ChatParticipantsChannel.objects.filter(user=self.user).delete()
