from django.db import models
from django.contrib.auth.models import AbstractUser
from locations.models import Location

class User(AbstractUser):
    """
    User model as specified in the Class Diagram.
    Acts as the base authentication model for all roles.
    """
    ROLE_CHOICES = (
        ('CITIZEN', 'Citizen / Volunteer'),
        ('REPORTER', 'Family Reporter'),
        ('POLICE', 'Police Officer'),
        ('ADMIN', 'Administrator'),
    )

    # In Class Diagram: userID: int [PK]
    userID = models.AutoField(primary_key=True)
    phone = models.CharField(max_length=20, blank=True, null=True, help_text="Emergency contact phone number")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='REPORTER')
    profilePicture = models.ImageField(upload_to='profile_photos/', blank=True, null=True, help_text="Profile picture")
    createdAt = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

    @property
    def is_officer(self):
        return hasattr(self, 'police_profile') or self.role == 'POLICE'

    @property
    def is_admin_user(self):
        return self.role == 'ADMIN' or self.is_superuser or self.is_staff

    @property
    def is_reporter(self):
        return hasattr(self, 'reporter_profile') or self.role == 'REPORTER'


class PoliceOfficer(models.Model):
    """
    PoliceOfficer model representing verified law enforcement.
    Assigned to verify reports, issue GD numbers, and validate sighting tips.
    """
    officerID = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='police_profile')
    badgeNumber = models.CharField(max_length=50, unique=True, help_text="Official Police Badge / BP Number")
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, blank=True, related_name='officers')
    stationName = models.CharField(max_length=120, help_text="Police Station / Thana Name e.g. Dhanmondi Thana")
    jurisdiction = models.CharField(max_length=120, help_text="Area covered e.g. Dhanmondi, Kalabagan")
    isVerified = models.BooleanField(default=True, help_text="Official badge verified by system admin")

    class Meta:
        verbose_name = "Police Officer"
        verbose_name_plural = "Police Officers"

    def __str__(self):
        return f"Officer {self.user.get_full_name() or self.user.username} - {self.badgeNumber} ({self.stationName})"

    @classmethod
    def createProfile(cls, user, badgeNumber, stationName, jurisdiction, location=None, isVerified=True):
        return cls.objects.create(
            user=user,
            badgeNumber=badgeNumber,
            stationName=stationName,
            jurisdiction=jurisdiction,
            location=location,
            isVerified=isVerified
        )

    def verifyReport(self, case, gdNumber, remarks=""):
        """Validates case and issues GD Number via verification app"""
        from verification.models import VerificationCheck
        from notifications.models import Notification

        verification, created = VerificationCheck.objects.get_or_create(case=case)
        verification.officer = self
        verification.assignGDNumber(gdNumber)
        verification.verifyStatus = 'APPROVED'
        verification.policeRemarks = remarks
        verification.save()

        # Update case status if needed
        if case.caseStatus == 'PENDING':
            case.caseStatus = 'SEARCHING'
            case.save()

        # Broadcast area alerts now that it's verified
        Notification.broadcastAreaAlert(case)
        return verification

    def updateGD(self, verification_check, new_gd_number):
        verification_check.gdNumber = new_gd_number
        verification_check.save()
        return verification_check

    def closeCase(self, case, status='FOUND'):
        case.caseStatus = status
        case.save()
        case.autoArchive()
        return case


class Reporter(models.Model):
    """
    Reporter model representing families or volunteers filing missing reports.
    """
    REPORTER_TYPE_CHOICES = (
        ('Family Member', 'Family Member'),
        ('Relative', 'Relative'),
        ('Legal Guardian', 'Legal Guardian'),
        ('Concerned Citizen', 'Concerned Citizen'),
        ('Community Volunteer', 'Community Volunteer'),
    )

    reporterID = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='reporter_profile')
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, blank=True, related_name='reporters')
    reporterType = models.CharField(max_length=50, choices=REPORTER_TYPE_CHOICES, default='Family Member')
    relation = models.CharField(max_length=80, blank=True, help_text="Relationship to missing person (e.g. Mother, Brother)")
    nidNumber = models.CharField(max_length=30, blank=True, help_text="National Identity (NID) Number for authenticity")
    isVerified = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Reporter"
        verbose_name_plural = "Reporters"

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} ({self.reporterType})"

    @classmethod
    def createProfile(cls, user, location=None, reporterType='Family Member', relation='', nidNumber='', isVerified=True):
        return cls.objects.create(
            user=user,
            location=location,
            reporterType=reporterType,
            relation=relation,
            nidNumber=nidNumber,
            isVerified=isVerified
        )

    def viewProfile(self):
        return {
            "reporterID": self.reporterID,
            "name": self.user.get_full_name() or self.user.username,
            "email": self.user.email,
            "phone": self.user.phone,
            "reporterType": self.reporterType,
            "relation": self.relation,
            "nid": self.nidNumber,
            "isVerified": self.isVerified
        }

    def submitCase(self, case_data, location):
        """Submit a new missing person report"""
        from cases.models import MissingPersonCase
        return MissingPersonCase.createCase(reporter=self, location=location, **case_data)

    def deleteProfile(self):
        self.delete()


import random
from datetime import timedelta

class PasswordResetCode(models.Model):
    """Stores 6-digit email verification codes for password resets"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reset_codes')
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Password Reset Code"
        verbose_name_plural = "Password Reset Codes"
        ordering = ['-created_at']

    def __str__(self):
        return f"Code for {self.user.username}: {self.code}"

    @classmethod
    def create_for_user(cls, user):
        code = f"{random.randint(100000, 999999)}"
        return cls.objects.create(user=user, code=code)

    def is_valid(self):
        from django.utils import timezone
        now = timezone.now()
        return not self.is_used and (now - self.created_at) < timedelta(minutes=15)
