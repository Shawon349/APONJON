from django.contrib import admin
from .models import Notification

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('notificationID', 'recipient', 'notificationType', 'priorityLevel', 'isRead', 'createdAt')
    list_filter = ('notificationType', 'priorityLevel', 'isRead')
    search_fields = ('title', 'message', 'recipient__username')
