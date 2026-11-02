from django.db import models
from django.utils import timezone
from cases.models import MissingPersonCase
from accounts.models import Reporter, User
from locations.models import Location

class SightingTip(models.Model):
    """
    SightingTip model as specified in the Class Diagram.
    Allows citizens, shopkeepers, and volunteers to submit sighting clues, photos, and places.
    """
    STATUS_CHOICES = (
        ('PENDING', 'Pending Verification'),
        ('CREDIBLE', 'Flagged as Credible Clue'),
        ('DISMISSED', 'Dismissed / False Lead'),
    )

    tipID = models.AutoField(primary_key=True)
    case = models.ForeignKey(MissingPersonCase, on_delete=models.CASCADE, related_name='sighting_tips')
    reporter = models.ForeignKey(Reporter, on_delete=models.SET_NULL, null=True, blank=True, related_name='submitted_tips', help_text="User/Reporter who submitted tip (optional for anonymous)")
    tipster_name = models.CharField(max_length=100, blank=True, help_text="Name or Anonymous")
    tipster_phone = models.CharField(max_length=20, blank=True, help_text="Contact number for verification")
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, blank=True, related_name='sighting_tips')
    
    sightingDescription = models.TextField(help_text="Where was the person spotted, what were they doing, who were they with?")
    sightingTime = models.DateTimeField(default=timezone.now, help_text="Estimated time of sighting")
    photoProof = models.ImageField(upload_to='sighting_proofs/', blank=True, null=True, help_text="Photo proof if captured")
    photoURL = models.URLField(max_length=500, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Sighting Tip"
        verbose_name_plural = "Sighting Tips"
        ordering = ['-sightingTime']

    def __str__(self):
        return f"Tip #{self.tipID} for Case #{self.case_id} [{self.status}]"

    @classmethod
    def createTip(cls, case, sightingDescription, sightingTime=None, location=None, reporter=None, photoProof=None, tipster_name='', tipster_phone=''):
        """Class method matching Class Diagram createTip()"""
        tip = cls.objects.create(
            case=case,
            sightingDescription=sightingDescription,
            sightingTime=sightingTime or timezone.now(),
            location=location,
            reporter=reporter,
            photoProof=photoProof,
            tipster_name=tipster_name,
            tipster_phone=tipster_phone,
            status='PENDING'
        )
        # Notify the case reporter and investigating officers
        from notifications.models import Notification
        if case.reporter and case.reporter.user:
            Notification.objects.create(
                recipient=case.reporter.user,
                case=case,
                notificationType='SIGHTING_TIP',
                title=f"New Sighting Tip for {case.fullName}",
                message=f"A citizen reported spotting {case.fullName} at {location.area if location else 'nearby'}. Status: Pending review.",
                priorityLevel='HIGH'
            )
        return tip

    def viewTip(self):
        return {
            "tipID": self.tipID,
            "case": self.case.fullName,
            "description": self.sightingDescription,
            "time": self.sightingTime,
            "location": str(self.location) if self.location else "Unknown",
            "status": self.status,
            "has_photo": bool(self.photoProof or self.photoURL)
        }

    def updateTipStatus(self, new_status):
        self.status = new_status
        self.save()
        return self

    def flagCredible(self):
        """Flags tip as credible and elevates case status to SIGHTED"""
        self.status = 'CREDIBLE'
        self.save()
        if self.case.caseStatus == 'SEARCHING':
            self.case.caseStatus = 'SIGHTED'
            self.case.save()
        
        # Dispatch notification
        from notifications.models import Notification
        if self.case.reporter and self.case.reporter.user:
            Notification.objects.create(
                recipient=self.case.reporter.user,
                case=self.case,
                notificationType='SIGHTING_TIP',
                title=f"Credible Lead Confirmed for {self.case.fullName}!",
                message=f"Police marked a sighting tip at {self.location.area if self.location else 'nearby'} as CREDIBLE.",
                priorityLevel='CRITICAL'
            )
        return True

    def cancelTip(self):
        self.status = 'DISMISSED'
        self.save()
        return True
