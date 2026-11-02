from django.urls import path
from . import views

app_name = 'verification'

urlpatterns = [
    path('queue/', views.verify_queue, name='verify_queue'),
    path('case/<int:pk>/', views.verify_case, name='verify_case'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('case/<int:pk>/admin-approve/', views.admin_approve_case, name='admin_approve_case'),
    path('case/<int:pk>/admin-decline/', views.admin_decline_case, name='admin_decline_case'),
]
