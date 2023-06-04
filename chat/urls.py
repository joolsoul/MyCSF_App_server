from django.urls import path
from .views import UserSearchAPIView, UserSelfId, RoomMessagesView, ChatRoomListView

urlpatterns = [
    path('users/search/', UserSearchAPIView.as_view(), name='search_users'),
    path('users/selfid/', UserSelfId.as_view(), name='self_id'),
    path('room-messages/<int:user_id>/', RoomMessagesView.as_view(), name='room_messages'),
    path('room-messages/<int:user_id>/<int:room_id>/', RoomMessagesView.as_view(), name='room_messages'),

    path('user-chatrooms/', ChatRoomListView.as_view(), name='user_chatrooms')
]