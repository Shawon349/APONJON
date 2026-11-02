from django.contrib import admin
from .models import Location

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('locationID', 'area', 'thana', 'city', 'latitude', 'longitude')
    search_fields = ('address', 'area', 'thana', 'city')
    list_filter = ('city', 'thana')
