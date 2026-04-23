from django.urls import path
from .views import (SendNotificationView,MyNotificationsView,MarkAsReadView,MarkAllAsReadView,)

urlpatterns = [
    path('notifications/send/', SendNotificationView.as_view(), name='send-notification'),
    path('notifications/my/', MyNotificationsView.as_view(), name='my-notifications'),
    path('notifications/<int:pk>/read/', MarkAsReadView.as_view(), name='mark-as-read'),
    path('notifications/read-all/', MarkAllAsReadView.as_view(), name='mark-all-read'),
]