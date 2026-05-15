from django.urls import path
from .views import (BroadcastCreateView,BroadcastListView,MyNotificationListView,MarkReadView,MarkAllReadView,UnreadCountView,BroadcastDeleteView,MyNotificationDeleteView)

urlpatterns = [
    path('broadcast/', BroadcastCreateView.as_view()),
    path('broadcast/list/', BroadcastListView.as_view()),
    path('my/', MyNotificationListView.as_view()),
    path('<int:pk>/read/', MarkReadView.as_view()),
    path('read-all/', MarkAllReadView.as_view()),
    path('unread-count/', UnreadCountView.as_view()),
    path('broadcast/<int:pk>/delete/', BroadcastDeleteView.as_view()),    
    path('my/<int:pk>/delete/', MyNotificationDeleteView.as_view()),
    
]