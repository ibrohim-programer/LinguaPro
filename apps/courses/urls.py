from django.urls import path
from .views import *
urlpatterns = [
    path('course-list/',CourseListView.as_view()),
    path('course-create/',CourseCreateView.as_view()),
    path('course-update-delete/<int:pk>',CourseUpdateDeleteView.as_view()),
]
