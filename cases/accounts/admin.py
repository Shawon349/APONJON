from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, PoliceOfficer, Reporter

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('userID', 'username', 'email', 'phone', 'role', 'is_staff', 'createdAt')
    list_filter = ('role', 'is_staff', 'is_superuser')
    fieldsets = UserAdmin.fieldsets + (
        ('Custom Info', {'fields': ('phone', 'role')}),
    )

@admin.register(PoliceOfficer)
class PoliceOfficerAdmin(admin.ModelAdmin):
    list_display = ('officerID', 'user', 'badgeNumber', 'stationName', 'jurisdiction', 'isVerified')
    list_filter = ('stationName', 'isVerified')
    search_fields = ('badgeNumber', 'stationName', 'jurisdiction', 'user__username', 'user__first_name', 'user__last_name')

@admin.register(Reporter)
class ReporterAdmin(admin.ModelAdmin):
    list_display = ('reporterID', 'user', 'reporterType', 'relation', 'nidNumber', 'isVerified')
    list_filter = ('reporterType', 'isVerified')
    search_fields = ('nidNumber', 'user__username', 'user__first_name', 'user__last_name')
