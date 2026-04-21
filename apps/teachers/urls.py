from django.urls import path
from .views import (
    TeacherListView,
    TeacherCreateView,
    TeacherDetailUpdateDeleteView,
    TeacherDashboardView,
)


urlpatterns = [
    path('teacher-list/',TeacherListView.as_view(),name='teacher_list'),
    path('teacher-create/',TeacherCreateView.as_view(),name='teacher_create'),
    path('teacher-update-delete/<int:pk>/',TeacherDetailUpdateDeleteView.as_view(),name='teacher_detail'),
    path('dashboard/', TeacherDashboardView.as_view(),name='teacher_dashboard'),
]