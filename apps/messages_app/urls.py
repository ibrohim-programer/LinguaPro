# urls.py
from django.urls import path
from .views import MyGroupListView,GroupMessageListView,SendGroupMessageView,DeleteGroupMessageView,UnreadCountView

urlpatterns = [
    path('', MyGroupListView.as_view(), name='my-chat-groups'),
    path('<int:group_id>/messages/', GroupMessageListView.as_view(), name='group-messages'),
    path('<int:group_id>/send/', SendGroupMessageView.as_view(), name='send-group-message'),
    path('<int:group_id>/messages/<int:message_id>/', DeleteGroupMessageView.as_view(), name='delete-group-message'),
    path('unread-count/', UnreadCountView.as_view(), name='unread-count'),
]