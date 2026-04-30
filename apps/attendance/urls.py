from django.urls import path
from .views import AttendanceListCreateView,AttendanceBulkUpdateView,MyAttendanceView,AttendanceStatsView

urlpatterns = [
    path('list', AttendanceListCreateView.as_view()),
    path('bulk-update/', AttendanceBulkUpdateView.as_view()),  
    path('my/', MyAttendanceView.as_view()),
    path('stats/<int:group_id>/', AttendanceStatsView.as_view()),
]