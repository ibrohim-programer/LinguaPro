from django.urls import path
from .views import *
urlpatterns = [
    path('list-admin/' , GroupListIsAdmin.as_view() , name='list-admin'),
    path('create-admin/' , GroupCreateIsAdmin.as_view() , name='create-admin'),
    path('update-delete-admin/<int:pk>/' , GroupUpdateDeleteIsAdmin.as_view() , name='update-delete-admin'),
    
    # Admin - Teacher
    path('my/', MyGroupsView.as_view(), name='my-groups'),
    path('<int:pk>/add-student/', AddStudentView.as_view(), name='add-student'),
    path('<int:pk>/remove-student/<int:sid>/', RemoveStudentView.as_view(),name='remove-student'),
    
    path('<int:pk>/available-students/', AvailableStudentsView.as_view(), name='available-students'),
    path('students-list/', StudentListView.as_view(), name='students-list'),
]




