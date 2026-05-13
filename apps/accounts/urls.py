from django.urls import path
from .views import RegisterView , LoginView,ForgotPasswordView , VerfiyPasswordView,ProfileView , ProfileUpdateView,ProfileDelete,UserListAdminView ,MyProfileLogoutView
urlpatterns = [
    # Auth
    path('login/',LoginView.as_view(),name='login'),
  
    # Verify password
    path('forgot-password/' , ForgotPasswordView.as_view() , name='forgot-password'),
    path('verfiy-password/' , VerfiyPasswordView.as_view() , name='verfiy-password'),
    
    # My Profile
    path("my-profile-list/" , ProfileView.as_view() ,name='profile-list'),
    path("my-profile-update/" , ProfileUpdateView.as_view() ,name='profile-update'),
    path("my-profile-logout/" , MyProfileLogoutView.as_view() ,name='profile-logout'),
    
    
    # IS_Admin
    path('register/',RegisterView.as_view(),name='register'),
    path('user-list/' , UserListAdminView.as_view() , name='user-list'),
    path("profile-delete/" , ProfileDelete.as_view() ,name='profile-delete'),
    
]