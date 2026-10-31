"""
URL configuration for aponjon_project.
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
from cases.views import home
from accounts import views as accounts_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('admin-portal/login/', accounts_views.admin_login, name='admin_portal_login'),
    path('admin-portal/register/', accounts_views.register_admin, name='admin_portal_register'),
    path('accounts/', include('accounts.urls')),
    path('cases/', include('cases.urls')),
    path('verification/', include('verification.urls')),
    path('sightings/', include('sightings.urls')),
    path('notifications/', include('notifications.urls')),
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
