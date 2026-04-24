from django.urls import path
from .views import *
urlpatterns = [
    path('list/',CourseListView.as_view()),
    path('create/',CourseCreateView.as_view()),
    path('update-delete/<int:pk>',CourseUpdateDeleteView.as_view()),
]
