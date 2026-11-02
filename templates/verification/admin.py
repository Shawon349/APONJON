from django.contrib import admin
from .models import VerificationCheck

@admin.register(VerificationCheck)
class VerificationCheckAdmin(admin.ModelAdmin):
    list_display = ('verificationID', 'case', 'gdNumber', 'verifyStatus', 'officer', 'verifiedAt')
    list_filter = ('verifyStatus',)
    search_fields = ('gdNumber', 'case__fullName', 'officer__badgeNumber')
