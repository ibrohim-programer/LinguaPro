from django.urls import path
from .views import (
    AttendanceListCreateView,
    AttendanceUpdateView,
    MyAttendanceView,
    AttendanceStatsView,
)

urlpatterns = [
    path('list', AttendanceListCreateView.as_view()),
    path('update/<int:pk>/', AttendanceUpdateView.as_view()),
    path('my/', MyAttendanceView.as_view()),
    path('stats/<int:group_id>/', AttendanceStatsView.as_view()),
]