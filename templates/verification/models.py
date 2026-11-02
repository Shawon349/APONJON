from django.db import models
from django.utils import timezone
from cases.models import MissingPersonCase
from accounts.models import PoliceOfficer

class VerificationCheck(models.Model):
    """
    VerificationCheck model as specified in the Class Diagram.
    Acts as the official police audit gatekeeper.
    Reports without police verification and GD number cannot broadcast area-wide panic alerts.
    """
    VERIFY_STATUS_CHOICES = (
        ('PENDING', 'Pending Police Verification'),
        ('APPROVED', 'Verified & GD Issued'),
        ('REJECTED', 'Rejected / False Report'),
        ('UNDER_INVESTIGATION', 'Under Preliminary Inquiry'),
        ('CLOSED', 'Verification Closed'),
    )

    verificationID = models.AutoField(primary_key=True)
    case = models.OneToOneField(MissingPersonCase, on_delete=models.CASCADE, related_name='verification')
    officer = models.ForeignKey(PoliceOfficer, on_delete=models.SET_NULL, null=True, blank=True, related_name='verifications')
    
    gdNumber = models.CharField(max_length=60, blank=True, null=True, unique=True, help_text="Official Police Station GD Number (e.g. GD-2026-DHAN-9841)")
    verifyStatus = models.CharField(max_length=30, choices=VERIFY_STATUS_CHOICES, default='PENDING')
    policeRemarks = models.TextField(blank=True, help_text="Notes from the investigating officer")
    verifiedAt = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Police Verification Check"
        verbose_name_plural = "Police Verification Checks"

    def __str__(self):
        return f"Verification #{self.verificationID} for Case #{self.case_id} [{self.verifyStatus}]"

    def validateCase(self):
        """Checks if case has necessary details and GD number to be approved"""
        if self.gdNumber and len(self.gdNumber.strip()) >= 4:
            self.verifyStatus = 'APPROVED'
            self.verifiedAt = timezone.now()
            self.save()
            return True
        return False

    def blockUnverified(self):
        """Blocks broadcast of unverified reports to prevent fake news & panic"""
        self.verifyStatus = 'REJECTED'
        self.save()
        return False

    def assignGDNumber(self, gd_num):
        """Assigns official General Diary number from Thana registry"""
        self.gdNumber = gd_num.strip()
        self.verifyStatus = 'APPROVED'
        self.verifiedAt = timezone.now()
        self.save()
        return self.gdNumber

    def closeVerification(self):
        self.verifyStatus = 'CLOSED'
        self.save()
