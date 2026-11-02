from django.contrib import admin
from .models import MissingPersonCase, PriorityTracker

@admin.register(MissingPersonCase)
class MissingPersonCaseAdmin(admin.ModelAdmin):
    list_display = ('caseID', 'fullName', 'age', 'gender', 'caseStatus', 'isArchived', 'created_at')
    list_filter = ('caseStatus', 'gender', 'isArchived')
    search_fields = ('fullName', 'clothingDetails', 'medicalConditions')

@admin.register(PriorityTracker)
class PriorityTrackerAdmin(admin.ModelAdmin):
    list_display = ('trackerID', 'case', 'urgencyLevel', 'reportedAt', 'alertSent')
    list_filter = ('urgencyLevel', 'alertSent')
