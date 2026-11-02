from django.contrib import admin
from .models import SightingTip

@admin.register(SightingTip)
class SightingTipAdmin(admin.ModelAdmin):
    list_display = ('tipID', 'case', 'status', 'sightingTime', 'tipster_name', 'tipster_phone')
    list_filter = ('status', 'sightingTime')
    search_fields = ('sightingDescription', 'case__fullName', 'tipster_name', 'tipster_phone')
