from django.urls import path
from . import views

urlpatterns = [
    path('list-create/',  views.AssignmentListCreateView.as_view()),
    path('my/',           views.MyAssignmentsView.as_view()),
    # YANGI: fayl yuklash endpointi
    path('upload/',       views.AssignmentFileUploadView.as_view(), name='assignment-file-upload'),
    path('<int:pk>/',     views.AssignmentDetailView.as_view()),
    path('<int:pk>/submit/', views.SubmitAssignmentView.as_view()),
    path('<int:pk>/grade/',  views.GradeSubmissionView.as_view()),
    path('<int:pk>/status/', views.AssignmentSubmissionStatusView.as_view()),
]