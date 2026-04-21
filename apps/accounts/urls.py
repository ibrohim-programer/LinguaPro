from django.urls import path
from .views import (RegisterView , LoginView,
                    ForgotPasswordView , VerfiyPasswordView,
                    ProfileView , ProfileUpdateView,
                    UserListAdminView
                    )
urlpatterns = [
    # Auth
    path('register/',RegisterView.as_view(),name='register'),
    path('login/',LoginView.as_view(),name='login'),
  
    # Verify password
    path('forgot-password/' , ForgotPasswordView.as_view() , name='forgot-password'),
    path('verfiy-password/' , VerfiyPasswordView.as_view() , name='verfiy-password'),
    
    # My Profile
    path("my-profile-list/" , ProfileView.as_view() ,name='profile-list'),
    path("my-profile-update-delete/" , ProfileUpdateView.as_view() ,name='profile-update-delete'),
    
    # IS_Admin
    path('user-list/' , UserListAdminView.as_view() , name='user-list')
    
]