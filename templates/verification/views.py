from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import VerificationCheck
from .forms import VerifyCaseForm
from cases.models import MissingPersonCase
from notifications.models import Notification

def is_admin_or_officer(user):
    return user.is_authenticated and (
        user.is_staff or 
        user.is_superuser or 
        user.role in ['ADMIN', 'POLICE'] or 
        hasattr(user, 'police_profile')
    )

@login_required
def verify_queue(request):
    """View of all missing person reports pending police verification"""
    if not is_admin_or_officer(request.user):
        messages.error(request, "এই পেজে প্রবেশের জন্য পুলিশ অফিসার বা অ্যাডমিনের অনুমতি প্রয়োজন।")
        return redirect('home')

    pending_checks = VerificationCheck.objects.filter(verifyStatus__in=['PENDING', 'UNDER_INVESTIGATION']).select_related('case', 'case__location', 'case__reporter').order_by('-case__created_at')
    
    return render(request, 'verification/verify_queue.html', {'pending_checks': pending_checks})


@login_required
def verify_case(request, pk):
    """
    Officer verifies report, assigns GD Number, and triggers area-based alerts.
    """
    if not is_admin_or_officer(request.user):
        messages.error(request, "এই পেজে প্রবেশের জন্য পুলিশ অফিসার বা অ্যাডমিনের অনুমতি প্রয়োজন।")
        return redirect('home')

    case = get_object_or_404(MissingPersonCase, pk=pk)
    verification, created = VerificationCheck.objects.get_or_create(case=case)
    officer_profile = getattr(request.user, 'police_profile', None)

    if request.method == 'POST':
        form = VerifyCaseForm(request.POST, instance=verification)
        if form.is_valid():
            check = form.save(commit=False)
            if officer_profile:
                check.officer = officer_profile
            check.verifiedAt = timezone.now()
            check.save()

            if check.verifyStatus == 'APPROVED':
                case.caseStatus = 'SEARCHING'
                case.save()
                
                # Broadcast area-wide public alerts
                Notification.broadcastAreaAlert(case)

                # Notify family reporter that their case has been verified
                Notification.objects.create(
                    recipient=case.reporter.user,
                    case=case,
                    notificationType='CASE_VERIFIED',
                    title=f"রিপোর্ট অনুমোদিত: জিডি #{check.gdNumber}",
                    message=f"{case.fullName}-এর নিখোঁজ রিপোর্টটি সরকারি জিডি নম্বর {check.gdNumber} সহ অনুমোদিত হয়েছে এবং এলাকায় এলার্ট পাঠানো হয়েছে।",
                    priorityLevel='HIGH'
                )

                messages.success(request, f"কেস #{case.caseID} সফলভাবে অনুমোদিত হয়েছে (জিডি #{check.gdNumber})! এলাকাভিত্তিক সতর্কতা পাঠানো হয়েছে।")
            elif check.verifyStatus == 'REJECTED':
                case.caseStatus = 'CLOSED'
                case.save()

                Notification.objects.create(
                    recipient=case.reporter.user,
                    case=case,
                    notificationType='CASE_RESOLVED',
                    title=f"কেস #{case.caseID} প্রত্যাখ্যান করা হয়েছে",
                    message=f"আপনার দাখিলকৃত রিপোর্টটি গ্রহণযোগ্য বিবেচিত হয়নি। কারণ: {check.policeRemarks or 'অপর্যাপ্ত তথ্য বা তথ্যের অমিল'}",
                    priorityLevel='STANDARD'
                )
                messages.warning(request, f"কেস #{case.caseID} প্রত্যাখ্যান করা হয়েছে।")

            if request.user.role == 'ADMIN' or request.user.is_superuser:
                return redirect('verification:admin_dashboard')
            return redirect('accounts:officer_dashboard')
    else:
        form = VerifyCaseForm(instance=verification)

    return render(request, 'verification/verify_case.html', {'form': form, 'case': case, 'verification': verification})


@login_required
def admin_dashboard(request):
    """
    Dedicated Admin Moderation Panel.
    Allows Admins to view all reports, approve with GD numbers, or decline with feedback.
    """
    if not (request.user.role == 'ADMIN' or request.user.is_superuser or request.user.is_staff):
        messages.error(request, "এই প্যানেলে প্রবেশের অনুমতি কেবল সিস্টেম অ্যাডমিনদের রয়েছে।")
        return redirect('home')

    pending_cases = MissingPersonCase.objects.filter(verification__verifyStatus='PENDING').order_by('-created_at')
    approved_cases = MissingPersonCase.objects.filter(verification__verifyStatus='APPROVED').order_by('-updated_at')
    declined_cases = MissingPersonCase.objects.filter(verification__verifyStatus='REJECTED').order_by('-updated_at')

    context = {
        'pending_cases': pending_cases,
        'approved_cases': approved_cases,
        'declined_cases': declined_cases,
    }
    return render(request, 'verification/admin_dashboard.html', context)


@login_required
def admin_approve_case(request, pk):
    """One-click or quick action to approve a post by Admin"""
    if not (request.user.role == 'ADMIN' or request.user.is_superuser or request.user.is_staff):
        messages.error(request, "অনুমতি নেই।")
        return redirect('home')

    case = get_object_or_404(MissingPersonCase, pk=pk)
    verification, _ = VerificationCheck.objects.get_or_create(case=case)

    gd_input = request.POST.get('gdNumber', '').strip()
    if not gd_input:
        gd_input = f"GD-2026-ADM-{case.pk:04d}"

    verification.gdNumber = gd_input
    verification.verifyStatus = 'APPROVED'
    verification.verifiedAt = timezone.now()
    verification.policeRemarks = request.POST.get('remarks', 'অ্যাডমিন কর্তৃক সরাসরি অনুমোদিত')
    verification.save()

    case.caseStatus = 'SEARCHING'
    case.save()

    Notification.broadcastAreaAlert(case)
    Notification.objects.create(
        recipient=case.reporter.user,
        case=case,
        notificationType='CASE_VERIFIED',
        title=f"পোস্ট অনুমোদিত: জিডি #{verification.gdNumber}",
        message=f"আপনার নিখোঁজ রিপোর্ট ({case.fullName}) অ্যাডমিন কর্তৃক অনুমোদিত হয়েছে এবং এলাকায় এলার্ট পাঠানো হয়েছে।",
        priorityLevel='HIGH'
    )

    messages.success(request, f"কেস #{case.caseID} সফলভাবে অনুমোদিত হয়েছে (জিডি: {verification.gdNumber})!")
    return redirect('verification:admin_dashboard')


@login_required
def admin_decline_case(request, pk):
    """Action to decline/reject a post by Admin"""
    if not (request.user.role == 'ADMIN' or request.user.is_superuser or request.user.is_staff):
        messages.error(request, "অনুমতি নেই।")
        return redirect('home')

    case = get_object_or_404(MissingPersonCase, pk=pk)
    verification, _ = VerificationCheck.objects.get_or_create(case=case)

    reason = request.POST.get('reason', 'তথ্যের অপর্যাপ্ততা বা ভুয়া তথ্যের সন্দেহে বাতিল করা হয়েছে।')
    verification.verifyStatus = 'REJECTED'
    verification.policeRemarks = reason
    verification.save()

    case.caseStatus = 'CLOSED'
    case.save()

    Notification.objects.create(
        recipient=case.reporter.user,
        case=case,
        notificationType='CASE_RESOLVED',
        title=f"কেস #{case.caseID} পোস্টটি বাতিল করা হয়েছে",
        message=f"{case.fullName}-এর রিপোর্টটি অ্যাডমিন কর্তৃক বাতিল করা হয়েছে। কারণ: {reason}",
        priorityLevel='STANDARD'
    )

    messages.warning(request, f"কেস #{case.caseID} বাতিল / প্রত্যাখ্যান করা হয়েছে।")
    return redirect('verification:admin_dashboard')
