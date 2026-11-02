from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('register/reporter/', views.register_reporter, name='register_reporter'),
    path('register/volunteer/', views.register_volunteer, name='register_volunteer'),
    path('register/officer/', views.register_officer, name='register_officer'),
    path('register/admin/', views.register_admin, name='register_admin'),
    path('admin/login/', views.admin_login, name='admin_login'),
    path('profile/', views.profile_view, name='profile'),
    path('password/reset/', views.reset_password_request, name='reset_password'),
    path('password/reset/verify/', views.reset_password_verify, name='reset_password_verify'),
    path('password/change/', views.change_password, name='change_password'),
    path('officer/dashboard/', views.officer_dashboard, name='officer_dashboard'),
]
