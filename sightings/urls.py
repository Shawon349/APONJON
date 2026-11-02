from django.urls import path
from . import views

app_name = 'sightings'

urlpatterns = [
    path('submit/<int:case_id>/', views.submit_tip, name='submit_tip'),
    path('tip/<int:tip_id>/flag-credible/', views.flag_tip_credible, name='flag_tip_credible'),
    path('tip/<int:tip_id>/dismiss/', views.dismiss_tip, name='dismiss_tip'),
]
