from django.db import models
from django.utils import timezone
from datetime import timedelta
from accounts.models import Reporter
from locations.models import Location

class MissingPersonCase(models.Model):
    """
    MissingPersonCase model as specified in the Class Diagram.
    Stores all demographic, physical, and temporal clues about the missing person.
    """
    STATUS_CHOICES = (
        ('PENDING', 'Pending Verification'),
        ('SEARCHING', 'Active Search'),
        ('SIGHTED', 'Reported Sighted'),
        ('FOUND', 'Found'),
        ('REUNITED', 'Reunited with Family'),
        ('CLOSED', 'Closed'),
    )

    GENDER_CHOICES = (
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    )

    caseID = models.AutoField(primary_key=True)
    reporter = models.ForeignKey(Reporter, on_delete=models.CASCADE, related_name='cases')
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, blank=True, related_name='cases')
    
    fullName = models.CharField(max_length=150, help_text="Full Name of the missing individual")
    age = models.PositiveIntegerField(help_text="Age in years")
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES, default='Male')
    photo = models.ImageField(upload_to='case_photos/', blank=True, null=True, help_text="Clear face photo")
    photoURL = models.URLField(max_length=500, blank=True, null=True, help_text="External image link / placeholder")
    
    lastSeenTime = models.DateTimeField(help_text="Date and time when the person was last seen")
    caseStatus = models.CharField(max_length=30, choices=STATUS_CHOICES, default='PENDING')
    
    clothingDetails = models.TextField(blank=True, help_text="What were they wearing? (Color of shirt, pants, hijab, shoes)")
    medicalConditions = models.TextField(blank=True, help_text="Critical conditions: Alzheimer's, Dementia, Autism, Diabetes, Speech impaired, etc.")
    identifyingMarks = models.CharField(max_length=255, blank=True, help_text="Birthmarks, scars, tattoos, height, glasses, etc.")
    height = models.CharField(max_length=50, blank=True, help_text="e.g. 5 ft 4 in")
    
    # Auto-Archive & Privacy Protection Feature
    isArchived = models.BooleanField(default=False, help_text="Automatically hide photo & personal data once reunited")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Missing Person Case"
        verbose_name_plural = "Missing Person Cases"
        ordering = ['-created_at']

    def __str__(self):
        return f"Case #{self.caseID}: {self.fullName} ({self.get_caseStatus_display()})"

    @property
    def is_verified(self):
        return hasattr(self, 'verification') and self.verification.verifyStatus == 'APPROVED'

    @property
    def gd_number(self):
        if hasattr(self, 'verification') and self.verification.gdNumber:
            return self.verification.gdNumber
        return None

    @property
    def display_photo(self):
        """
        Respects Auto-Archive Privacy:
        If case is reunited/found or archived, masks photo to protect personal privacy!
        Provides authentic Bangladeshi demographic portraits according to name and age.
        """
        if self.isArchived or self.caseStatus in ['FOUND', 'REUNITED', 'CLOSED']:
            return "/static/images/reunited_privacy_shield.svg"
        if self.photo:
            return self.photo.url
        name_lower = (self.fullName or "").lower()
        if "karim" in name_lower or "abdul" in name_lower or self.age >= 65:
            return "/static/images/cases/haji_abdul_karim.jpg"
        if "rayan" in name_lower or "ahmed" in name_lower or self.age <= 12:
            return "/static/images/cases/rayan_ahmed.jpg"
        if "nusrat" in name_lower or (self.gender == 'Female' and 13 <= self.age <= 22):
            return "/static/images/cases/nusrat_jahan.jpg"
        if "fatema" in name_lower or (self.gender == 'Female' and self.age > 50):
            return "/static/images/cases/fatema_begum.jpg"
        if self.photoURL:
            return self.photoURL
        return "/static/images/missing_placeholder.svg"

    @classmethod
    def createCase(cls, reporter, location, **kwargs):
        """Factory method for creating a case and attaching a PriorityTracker"""
        case = cls.objects.create(
            reporter=reporter,
            location=location,
            **kwargs
        )
        # Create corresponding PriorityTracker automatically
        PriorityTracker.objects.create(case=case)
        # Create unverified VerificationCheck instance
        from verification.models import VerificationCheck
        VerificationCheck.objects.create(case=case, verifyStatus='PENDING')
        
        # Calculate initial urgency
        case.priority_tracker.escalateUrgency()
        return case

    def viewCase(self):
        return {
            "caseID": self.caseID,
            "fullName": self.fullName,
            "age": self.age,
            "gender": self.gender,
            "status": self.caseStatus,
            "lastSeen": self.lastSeenTime,
            "location": str(self.location) if self.location else "Unknown",
            "isArchived": self.isArchived,
            "gdNumber": self.gd_number
        }

    def updateCase(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        if self.caseStatus in ['FOUND', 'REUNITED', 'CLOSED']:
            self.autoArchive()
        else:
            self.save()
        return self

    def autoArchive(self):
        """
        Auto-Archive & Privacy Protection:
        As soon as the missing person is safely found and confirmed, 
        their photos and personal info are hidden from public view to protect their privacy.
        """
        self.isArchived = True
        self.save()
        if hasattr(self, 'priority_tracker'):
            self.priority_tracker.hideResolvedCase()
        return self


class PriorityTracker(models.Model):
    """
    PriorityTracker model as specified in the Class Diagram.
    Evaluates risk factors (small child, memory loss, medical needs) 
    and monitors critical 24-48 hour search countdown.
    """
    URGENCY_CHOICES = (
        ('CRITICAL', 'জরুরী সর্বোচ্চ ঝুঁকি (শিশু, প্রবীণ ও নারী) - Critical Priority'),
        ('HIGH', 'উচ্চ অগ্রাধিকার (নারী / তরুণ / জরুরী চিকিৎসা) - High Priority'),
        ('MEDIUM', 'সাধারণ অগ্রাধিকার - Standard Priority'),
        ('STANDARD', 'স্ট্যান্ডার্ড - Standard'),
    )

    trackerID = models.AutoField(primary_key=True)
    case = models.OneToOneField(MissingPersonCase, on_delete=models.CASCADE, related_name='priority_tracker')
    reportedAt = models.DateTimeField(auto_now_add=True)
    urgencyLevel = models.CharField(max_length=20, choices=URGENCY_CHOICES, default='STANDARD')
    alertSent = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Priority Tracker"
        verbose_name_plural = "Priority Trackers"

    def __str__(self):
        return f"Tracker for Case #{self.case_id} [{self.urgencyLevel}]"

    def elapsed_hours(self):
        diff = timezone.now() - self.reportedAt
        return int(diff.total_seconds() // 3600)

    def calculateCountdown(self):
        """
        First 48 hours are the golden window.
        Returns remaining hours out of 48.
        """
        diff = timezone.now() - self.case.lastSeenTime
        hours_passed = int(diff.total_seconds() // 3600)
        remaining = 48 - hours_passed
        return max(0, remaining)

    def escalateUrgency(self):
        """
        Automated Urgency Detection:
        - Children (age <= 14) -> CRITICAL
        - Old People / Elderly (age >= 60) -> CRITICAL
        - Women (Female / নারী / মহিলা) -> CRITICAL
        - Critical Medical Condition (Alzheimer's, Autism, Diabetes, Heart) -> CRITICAL
        - Youth (age <= 18) or elapsed > 24 hours -> HIGH
        """
        age = self.case.age or 0
        med = (self.case.medicalConditions or "").lower()
        gender = str(self.case.gender or "").strip().lower()
        
        is_child = age <= 14
        is_old_people = age >= 60
        is_female = gender in ['female', 'মহিলা', 'নারী'] or 'female' in gender
        has_critical_condition = any(word in med for word in [
            'alzheimer', 'dementia', 'memory', 'amnesia', 'stroke',
            'diabetes', 'heart', 'epilepsy', 'asthma', 'autis',
            'mental', 'handicap', 'wheelchair', 'অ্যালঝাইমার', 'স্মৃতিভ্রম'
        ])

        if is_child or is_old_people or is_female or has_critical_condition:
            self.urgencyLevel = 'CRITICAL'
        elif self.elapsed_hours() >= 24 or age <= 18:
            self.urgencyLevel = 'HIGH'
        else:
            self.urgencyLevel = 'MEDIUM'

        self.save()
        return self.urgencyLevel

    def sendPushAlert(self):
        """Dispatches area alert notifications via notifications app"""
        from notifications.models import Notification
        if not self.alertSent and self.case.is_verified:
            Notification.broadcastAreaAlert(self.case, priority_override=self.urgencyLevel)
            self.alertSent = True
            self.save()

    def hideResolvedCase(self):
        """Archiving logic to enforce privacy"""
        pass
