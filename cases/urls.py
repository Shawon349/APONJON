from django.urls import path
from . import views

app_name = 'cases'

urlpatterns = [
    path('', views.case_list, name='case_list'),
    path('create/', views.case_create, name='case_create'),
    path('my-cases/', views.my_cases, name='my_cases'),
    path('<int:pk>/', views.case_detail, name='case_detail'),
    path('<int:pk>/edit/', views.case_edit, name='case_edit'),
    path('<int:pk>/delete/', views.case_delete, name='case_delete'),
    path('<int:pk>/update-status/', views.case_update_status, name='case_update_status'),
]
