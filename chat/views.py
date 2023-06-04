from django.db.models import Q
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.status import HTTP_200_OK
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import LimitOffsetPagination
from .models import User, ChatRoomParticipants, Messages
from .serializers import ChatUserSerializer


class RoomMessagesView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, user_id, room_id=None):
        user = request.user

        if room_id:
            messages = list(Messages.objects.filter(room__id=room_id).values(
                'id', 'room', 'user', 'content', 'created_at'))
        else:
            messages = list(Messages.objects.filter(Q(room__name=f'{user.id}-{user_id}') |
                            Q(room__name=f'{user_id}-{user.id}')).values('id', 'room', 'user', 'content', 'created_at'))

        response_content = {
            'status': True,
            'message': 'Chat Room Messages',
            'data': messages
        }

        return Response(response_content, status=status.HTTP_200_OK)


class ChatRoomListView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user = request.user

        chatroomparticipants = ChatRoomParticipants

        # room_ids = list(chatroomparticipants.object)

        room_ids = list(ChatRoomParticipants.objects.filter(
            user=user).values_list('room__id', flat=True))
        chatrooms = list(ChatRoomParticipants.objects.exclude(user__id=user.id).filter(
            room__id__in=room_ids).values('user__username', 'user__avatar', 'user__first_name', 'user__second_name', 'user__patronymic', 'user__id', 'room__id', 'room__name', 'room__last_message', 'room__last_sent_user'))

        scheme = request.is_secure() and "https" or "http"
        host = request.get_host()

        for chatroom in chatrooms:
            if chatroom["user__avatar"]:
                full_path = f'{scheme}://{host}/media/{chatroom["user__avatar"]}'
                chatroom["user__avatar"] = full_path

        response_content = {
            'status': True,
            'message': 'User Chat Room List',
            'data': chatrooms
        }

        return Response(response_content, status=status.HTTP_200_OK)


class UserSearchAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        u = self.request.user
        query = request.GET.get('query', '')
        limit = request.GET.get('limit', 10)
        offset = request.GET.get('offset', 0)

        paginator = LimitOffsetPagination()
        paginator.default_limit = limit
        paginator.offset = offset

        users = User.objects.filter(
            first_name__istartswith=query) | User.objects.filter(
            second_name__istartswith=query) | User.objects.filter(
            patronymic__istartswith=query) | User.objects.filter(
            username__istartswith=query)

        users = users.exclude(id=u.id)

        paginated_users = paginator.paginate_queryset(users, request)

        serializer = ChatUserSerializer(paginated_users, many=True, context={'request': request})

        return paginator.get_paginated_response(serializer.data)


class UserSelfId(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"id": self.request.user.id}, status=HTTP_200_OK)