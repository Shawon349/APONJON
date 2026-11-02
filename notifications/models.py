from django.db import models
from accounts.models import User
from cases.models import MissingPersonCase

class Notification(models.Model):
    """
    Notification model as specified in the Class Diagram.
    Manages area-targeted alerts, critical urgency pushes, and case status updates.
    """
    NOTIFICATION_TYPE_CHOICES = (
        ('URGENT_ALERT', 'Urgent Missing Person Alert'),
        ('AREA_ALERT', 'Area Neighborhood Alert'),
        ('SIGHTING_TIP', 'Sighting Clue Update'),
        ('CASE_VERIFIED', 'Police Verification Approved'),
        ('CASE_RESOLVED', 'Missing Person Safely Found'),
    )

    PRIORITY_LEVEL_CHOICES = (
        ('CRITICAL', 'Critical (Child / Medical / Elderly)'),
        ('HIGH', 'High'),
        ('MEDIUM', 'Medium'),
        ('STANDARD', 'Standard'),
    )

    notificationID = models.AutoField(primary_key=True)
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    case = models.ForeignKey(MissingPersonCase, on_delete=models.CASCADE, related_name='notifications', null=True, blank=True)
    
    notificationType = models.CharField(max_length=40, choices=NOTIFICATION_TYPE_CHOICES, default='AREA_ALERT')
    title = models.CharField(max_length=200)
    message = models.TextField()
    priorityLevel = models.CharField(max_length=20, choices=PRIORITY_LEVEL_CHOICES, default='HIGH')
    isRead = models.BooleanField(default=False)
    createdAt = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"
        ordering = ['-createdAt']

    def __str__(self):
        return f"[{self.priorityLevel}] {self.title} to {self.recipient.username}"

    @classmethod
    def createNotification(cls, recipient, title, message, case=None, notificationType='AREA_ALERT', priorityLevel='HIGH'):
        """Class method matching Class Diagram createNotification()"""
        return cls.objects.create(
            recipient=recipient,
            case=case,
            title=title,
            message=message,
            notificationType=notificationType,
            priorityLevel=priorityLevel
        )

    def viewNotification(self):
        return {
            "notificationID": self.notificationID,
            "title": self.title,
            "message": self.message,
            "priority": self.priorityLevel,
            "type": self.notificationType,
            "isRead": self.isRead,
            "time": self.createdAt
        }

    @classmethod
    def broadcastAreaAlert(cls, case, priority_override=None):
        """
        Broadcasts fast, area-based emergency alerts to citizens, volunteers, 
        and police officers in the same neighborhood or thana.
        """
        priority = priority_override
        if not priority and hasattr(case, 'priority_tracker'):
            priority = case.priority_tracker.urgencyLevel
        if not priority:
            priority = 'HIGH'

        loc_str = str(case.location) if case.location else "your area"
        title = f"EMERGENCY ALERT: Missing in {case.location.thana if case.location else 'Dhaka'} - {case.fullName}"
        message = (
            f"Verified Alert: {case.fullName} (Age {case.age}, {case.gender}) was last seen at {loc_str}. "
            f"Wearing: {case.clothingDetails or 'Not specified'}. "
            f"If you spot this person, submit a sighting tip immediately!"
        )

        recipients = set()
        if case.location:
            nearby = case.location.findNearbyUsers(radius_km=15.0)
            recipients.update(nearby)

        # Fallback: if no nearby users registered yet, notify all active users
        if not recipients:
            recipients = set(User.objects.all())

        notifications_to_create = []
        for user in recipients:
            notifications_to_create.append(
                cls(
                    recipient=user,
                    case=case,
                    notificationType='AREA_ALERT' if priority != 'CRITICAL' else 'URGENT_ALERT',
                    title=title,
                    message=message,
                    priorityLevel=priority
                )
            )

        if notifications_to_create:
            cls.objects.bulk_create(notifications_to_create)

        return len(notifications_to_create)

    def markAsRead(self):
        self.isRead = True
        self.save()
        return True
