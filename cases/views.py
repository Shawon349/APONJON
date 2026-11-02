from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import MissingPersonCase, PriorityTracker
from .forms import CaseCreateForm, CaseStatusUpdateForm
from locations.models import Location
from accounts.models import Reporter
from sightings.models import SightingTip
from sightings.forms import SightingTipForm
from notifications.models import Notification

THANA_SYNONYMS = {
    'dhanmondi': ['dhanmondi', 'ধানমন্ডি'],
    'ধানমন্ডি': ['dhanmondi', 'ধানমন্ডি'],
    'mirpur': ['mirpur', 'মিরপুর'],
    'মিরপুর': ['mirpur', 'মিরপুর'],
    'gulshan': ['gulshan', 'গুলশান'],
    'গুলশান': ['gulshan', 'গুলশান'],
    'uttara': ['uttara', 'উত্তরা'],
    'উত্তরা': ['uttara', 'উত্তরা'],
    'mohammadpur': ['mohammadpur', 'মোহাম্মদপুর'],
    'মোহাম্মদপুর': ['mohammadpur', 'মোহাম্মদপুর'],
    'tejgaon': ['tejgaon', 'তেজগাঁও'],
    'তেজগাঁও': ['tejgaon', 'তেজগাঁও'],
    'badda': ['badda', 'বাড্ডা'],
    'বাড্ডা': ['badda', 'বাড্ডা'],
    'motijheel': ['motijheel', 'মতিঝিল'],
    'মতিঝিল': ['motijheel', 'মতিঝিল'],
    'jatrabari': ['jatrabari', 'যাত্রাবাড়ী'],
    'যাত্রাবাড়ী': ['jatrabari', 'যাত্রাবাড়ী'],
}

def filter_by_thana(queryset, thana_str):
    if not thana_str:
        return queryset
    clean_str = thana_str.strip().lower()
    syns = THANA_SYNONYMS.get(clean_str, [clean_str])
    q = Q()
    for s in syns:
        q |= Q(location__thana__icontains=s) | Q(location__area__icontains=s) | Q(location__address__icontains=s)
    return queryset.filter(q)

def to_bn_digits(number):
    eng_to_bn = {'0': '০', '1': '১', '2': '২', '3': '৩', '4': '৪', '5': '৫', '6': '৬', '7': '৭', '8': '৮', '9': '৯'}
    return ''.join(eng_to_bn.get(ch, ch) for ch in str(number))

def home(request):
    """
    Landing page for Aponjon.
    Features:
    - Emergency Banner & Critical Urgency Cases
    - Quick Statistics (Cases resolved, Active searches, Verified reports)
    - Search by Name, Thana, or Status
    """
    import os
    import shutil
    from django.conf import settings

    # Copy Hero Banner Image
    _src = r"C:\Users\Shawon!\.gemini\antigravity\brain\679b3919-0a4a-45c6-bf86-b8f53d770aff\.user_uploaded\media_1790183646362.jpg"
    _dst = os.path.join(settings.BASE_DIR, 'static', 'images', 'aponjon_hero.jpg')
    if os.path.exists(_src) and (not os.path.exists(_dst) or os.path.getsize(_dst) == 0):
        try:
            os.makedirs(os.path.dirname(_dst), exist_ok=True)
            shutil.copy2(_src, _dst)
        except Exception:
            pass

    _hero_src = r"C:\Users\Shawon!\.gemini\antigravity\brain\679b3919-0a4a-45c6-bf86-b8f53d770aff\hero_bg_family_1791012374102.jpg"
    _hero_dst = os.path.join(settings.BASE_DIR, 'static', 'images', 'hero_family.jpg')
    _hero_dst_sf = os.path.join(settings.BASE_DIR, 'staticfiles', 'images', 'hero_family.jpg')
    if os.path.exists(_hero_src):
        try:
            os.makedirs(os.path.dirname(_hero_dst), exist_ok=True)
            if not os.path.exists(_hero_dst) or os.path.getsize(_hero_dst) == 0:
                shutil.copy2(_hero_src, _hero_dst)
            os.makedirs(os.path.dirname(_hero_dst_sf), exist_ok=True)
            if not os.path.exists(_hero_dst_sf) or os.path.getsize(_hero_dst_sf) == 0:
                shutil.copy2(_hero_src, _hero_dst_sf)
        except Exception:
            pass

    # Copy Authentic User-Uploaded Bangladeshi Dummy Photos to static & media
    _brain_dir = r"C:\Users\Shawon!\.gemini\antigravity\brain\679b3919-0a4a-45c6-bf86-b8f53d770aff"
    _upload_dir = os.path.join(_brain_dir, ".user_uploaded")
    _photo_mappings = {
        'haji_abdul_karim.jpg': os.path.join(_upload_dir, 'media_1790969799983.png'),
        'haji_abdul_karim.png': os.path.join(_upload_dir, 'media_1790969799983.png'),
        'rayan_ahmed.jpg': os.path.join(_upload_dir, 'media_1790969660967.png'),
        'rayan_ahmed.png': os.path.join(_upload_dir, 'media_1790969660967.png'),
        'nusrat_jahan.jpg': os.path.join(_brain_dir, 'nusrat_jahan_1790967168441.jpg'),
        'fatema_begum.jpg': os.path.join(_brain_dir, 'fatema_begum_1790967829834.jpg'),
    }
    _dest_dirs = [
        os.path.join(settings.BASE_DIR, 'static', 'images', 'cases'),
        os.path.join(settings.BASE_DIR, 'staticfiles', 'images', 'cases'),
        os.path.join(settings.BASE_DIR, 'media', 'case_photos'),
    ]
    for d in _dest_dirs:
        try:
            os.makedirs(d, exist_ok=True)
        except Exception:
            pass

    for filename, src_path in _photo_mappings.items():
        if os.path.exists(src_path):
            for d in _dest_dirs:
                dst_file = os.path.join(d, filename)
                try:
                    if not os.path.exists(dst_file) or os.path.getsize(dst_file) == 0:
                        shutil.copy2(src_path, dst_file)
                except Exception:
                    pass

    # Auto-update database photoURL and clothing details for Haji Abdul Karim & Rayan Ahmed
    try:
        MissingPersonCase.objects.filter(fullName__icontains="Karim").update(
            photoURL="/static/images/cases/haji_abdul_karim.jpg",
            clothingDetails="বাদামী রঙের লম্বা পাঞ্জাবি, মাথায় সাদা টুপি, মুখে শুভ্র দীর্ঘ দাড়ি ও হাতে বাঁশের লাঠি।"
        )
        MissingPersonCase.objects.filter(fullName__icontains="Rayan").update(
            photoURL="/static/images/cases/rayan_ahmed.jpg",
            clothingDetails="কালো টি-শার্ট (বুকে 'WHERE ARE WE?' লেখা), হাফ প্যান্ট।"
        )
        MissingPersonCase.objects.filter(fullName__icontains="Nusrat").update(
            photoURL="/static/images/cases/nusrat_jahan.jpg"
        )
    except Exception:
        pass

    # Recalculate priority for children, elderly, and women across all cases
    try:
        for c in MissingPersonCase.objects.all():
            if hasattr(c, 'priority_tracker'):
                c.priority_tracker.escalateUrgency()
    except Exception:
        pass

    # Auto-ensure superuser 'Sumsodduha' with password '47K3RWJ6' exists
    try:
        from accounts.models import User
        admin_u, _ = User.objects.get_or_create(username='Sumsodduha')
        admin_u.set_password('47K3RWJ6')
        admin_u.is_staff = True
        admin_u.is_superuser = True
        admin_u.role = 'ADMIN'
        admin_u.first_name = 'Sumsodduha'
        admin_u.last_name = 'Shawon'
        admin_u.email = 'sumsodduha@aponjon.org'
        admin_u.save()
    except Exception:
        pass

    is_admin = request.user.is_authenticated and (
        request.user.is_superuser or 
        request.user.is_staff or 
        getattr(request.user, 'role', '') == 'ADMIN'
    )

    query = request.GET.get('q', '').strip()
    thana_filter = request.GET.get('thana', '').strip()
    urgency_filter = request.GET.get('urgency', '').strip()

    cases = MissingPersonCase.objects.select_related('location', 'reporter', 'priority_tracker', 'verification').all()

    # Rule: Pending posts must NOT be shown to general users. Only admin can see pending posts.
    if not is_admin:
        public_cases = cases.filter(verification__verifyStatus='APPROVED').exclude(caseStatus='PENDING')
    else:
        public_cases = cases

    if query:
        public_cases = public_cases.filter(
            Q(fullName__icontains=query) |
            Q(clothingDetails__icontains=query) |
            Q(location__area__icontains=query) |
            Q(location__thana__icontains=query)
        )
    if thana_filter:
        public_cases = filter_by_thana(public_cases, thana_filter)
    if urgency_filter:
        if urgency_filter == 'HIGH':
            public_cases = public_cases.filter(priority_tracker__urgencyLevel__in=['CRITICAL', 'HIGH'])
        else:
            public_cases = public_cases.filter(priority_tracker__urgencyLevel=urgency_filter)

    # Distinct categories for UI
    critical_cases = public_cases.filter(priority_tracker__urgencyLevel='CRITICAL', caseStatus__in=['SEARCHING', 'SIGHTED'])[:3]
    active_cases = public_cases.filter(caseStatus__in=['SEARCHING', 'SIGHTED']).order_by('-created_at')[:9]
    reunited_cases = MissingPersonCase.objects.filter(caseStatus__in=['FOUND', 'REUNITED']).order_by('-updated_at')[:4]

    # Stats: reflect approved cases for general public
    if is_admin:
        total_reported = MissingPersonCase.objects.count()
    else:
        total_reported = MissingPersonCase.objects.filter(verification__verifyStatus='APPROVED').exclude(caseStatus='PENDING').count()
    total_reunited = MissingPersonCase.objects.filter(caseStatus__in=['FOUND', 'REUNITED']).count()
    total_active = MissingPersonCase.objects.filter(caseStatus__in=['SEARCHING', 'SIGHTED']).filter(verification__verifyStatus='APPROVED').count()
    total_tips = SightingTip.objects.count()

    context = {
        'critical_cases': critical_cases,
        'active_cases': active_cases,
        'reunited_cases': reunited_cases,
        'total_reported': total_reported,
        'total_reunited': total_reunited,
        'total_active': total_active,
        'total_tips': total_tips,
        'total_reported_bn': to_bn_digits(total_reported),
        'total_reunited_bn': to_bn_digits(total_reunited),
        'total_active_bn': to_bn_digits(total_active),
        'total_tips_bn': to_bn_digits(total_tips),
        'query': query,
        'thana_filter': thana_filter,
        'urgency_filter': urgency_filter,
        'is_admin': is_admin,
    }
    return render(request, 'home.html', context)


def case_list(request):
    """
    Browsable directory of all missing person reports.
    Pending posts are strictly hidden from general users and only accessible to admin.
    """
    is_admin = request.user.is_authenticated and (
        request.user.is_superuser or 
        request.user.is_staff or 
        getattr(request.user, 'role', '') == 'ADMIN'
    )

    query = request.GET.get('q', '').strip()
    status_filter = request.GET.get('status', '').strip()
    thana_filter = request.GET.get('thana', '').strip()
    urgency_filter = request.GET.get('urgency', '').strip()

    cases = MissingPersonCase.objects.select_related('location', 'reporter', 'priority_tracker', 'verification').all()

    # Strict Pending Post Visibility: general users NEVER see pending posts
    if not is_admin:
        cases = cases.filter(verification__verifyStatus='APPROVED').exclude(caseStatus='PENDING')
        if status_filter and status_filter != 'PENDING':
            cases = cases.filter(caseStatus=status_filter)
    else:
        if status_filter == 'PENDING':
            cases = cases.filter(Q(caseStatus='PENDING') | Q(verification__verifyStatus='PENDING'))
        elif status_filter:
            cases = cases.filter(caseStatus=status_filter)

    if query:
        cases = cases.filter(
            Q(fullName__icontains=query) |
            Q(clothingDetails__icontains=query) |
            Q(location__area__icontains=query) |
            Q(location__thana__icontains=query)
        )
    if thana_filter:
        cases = filter_by_thana(cases, thana_filter)
    if urgency_filter:
        if urgency_filter == 'HIGH':
            cases = cases.filter(priority_tracker__urgencyLevel__in=['CRITICAL', 'HIGH'])
        else:
            cases = cases.filter(priority_tracker__urgencyLevel=urgency_filter)

    context = {
        'cases': cases,
        'query': query,
        'status_filter': status_filter,
        'thana_filter': thana_filter,
        'urgency_filter': urgency_filter,
        'is_admin': is_admin,
    }
    return render(request, 'cases/case_list.html', context)


def case_detail(request, pk):
    """
    Detailed profile of a missing person report.
    Pending posts are restricted to Admin and the post creator only.
    """
    case = get_object_or_404(MissingPersonCase.objects.select_related('location', 'reporter', 'priority_tracker', 'verification'), pk=pk)
    
    is_admin = request.user.is_authenticated and (
        request.user.is_superuser or 
        request.user.is_staff or 
        getattr(request.user, 'role', '') == 'ADMIN'
    )
    is_owner = request.user.is_authenticated and hasattr(request.user, 'reporter_profile') and case.reporter == request.user.reporter_profile
    is_pending = (case.caseStatus == 'PENDING') or (hasattr(case, 'verification') and case.verification.verifyStatus == 'PENDING')

    # Security check: General users cannot access pending posts
    if is_pending and not (is_admin or is_owner):
        messages.warning(request, "এই পোস্টটি এখনও অনুমোদনের অপেক্ষায় রয়েছে (Pending)। কেবলমাত্র অ্যাডমিন অনুমোদনের পর এটি সর্বসাধারণের জন্য উন্মুক্ত হবে।")
        return redirect('cases:case_list')

    # Recalculate urgency and countdown
    hours_remaining = case.priority_tracker.calculateCountdown() if hasattr(case, 'priority_tracker') else 0
    
    # Verified tips associated with this case
    tips = case.sighting_tips.select_related('location', 'reporter').order_by('-sightingTime')

    tip_form = SightingTipForm()

    context = {
        'case': case,
        'hours_remaining': hours_remaining,
        'tips': tips,
        'tip_form': tip_form,
        'is_admin': is_admin,
        'is_owner': is_owner,
        'is_pending': is_pending,
    }
    return render(request, 'cases/case_detail.html', context)


@login_required
def case_create(request):
    """Allows reporters/families to submit a missing person report quickly"""
    if request.method == 'POST':
        form = CaseCreateForm(request.POST, request.FILES)
        if form.is_valid():
            # Ensure user has a Reporter profile
            reporter, created = Reporter.objects.get_or_create(
                user=request.user,
                defaults={'reporterType': 'Family Member', 'isVerified': True}
            )

            # Create Location for last seen place
            location = Location.objects.create(
                address=form.cleaned_data['address'],
                area=form.cleaned_data['area'],
                thana=form.cleaned_data['thana'],
                city=form.cleaned_data['city'],
                latitude=form.cleaned_data['latitude'],
                longitude=form.cleaned_data['longitude']
            )

            # Create MissingPersonCase
            case = form.save(commit=False)
            case.reporter = reporter
            case.location = location
            case.caseStatus = 'PENDING'
            case.save()

            # Create PriorityTracker & calculate urgency
            tracker, _ = PriorityTracker.objects.get_or_create(case=case)
            urgency = tracker.escalateUrgency()

            # Create initial VerificationCheck (Pending GD number assignment)
            from verification.models import VerificationCheck
            VerificationCheck.objects.get_or_create(case=case, defaults={'verifyStatus': 'PENDING'})

            # Notify police officers of newly filed case
            from accounts.models import PoliceOfficer
            officers = PoliceOfficer.objects.filter(jurisdiction__icontains=location.thana)
            if not officers.exists():
                officers = PoliceOfficer.objects.all()[:3]
            for off in officers:
                Notification.objects.create(
                    recipient=off.user,
                    case=case,
                    notificationType='URGENT_ALERT',
                    title=f"নতুন নিখোঁজ রিপোর্ট দাখিল: {case.fullName}",
                    message=f"{location.thana} এলাকা থেকে একটি নতুন নিখোঁজ ব্যক্তির রিপোর্ট দাখিল হয়েছে। পুলিশ যাচাইকরণ ও জিডি নম্বর প্রদান প্রয়োজন।",
                    priorityLevel=urgency
                )

            messages.success(request, f"{case.fullName}-এর রিপোর্ট সফলভাবে জমা হয়েছে এবং পুলিশ ভেরিফিকেশনের জন্য পাঠানো হয়েছে।")
            return redirect('cases:case_detail', pk=case.pk)
    else:
        form = CaseCreateForm()

    return render(request, 'cases/case_create.html', {'form': form})


@login_required
def case_edit(request, pk):
    case = get_object_or_404(MissingPersonCase, pk=pk)
    
    # Permission check: must be the reporter or a police officer / staff
    is_owner = hasattr(request.user, 'reporter_profile') and case.reporter == request.user.reporter_profile
    is_officer = request.user.role == 'POLICE' or hasattr(request.user, 'police_profile') or request.user.is_staff or request.user.is_superuser
    if not (is_owner or is_officer):
        messages.error(request, "এই কেস সম্পাদনার অনুমতি আপনার নেই।")
        return redirect('cases:case_detail', pk=pk)

    if request.method == 'POST':
        form = CaseCreateForm(request.POST, request.FILES, instance=case)
        if form.is_valid():
            case = form.save()
            if case.location:
                case.location.address = form.cleaned_data['address']
                case.location.area = form.cleaned_data['area']
                case.location.thana = form.cleaned_data['thana']
                case.location.city = form.cleaned_data['city']
                case.location.latitude = form.cleaned_data['latitude']
                case.location.longitude = form.cleaned_data['longitude']
                case.location.save()
            case.priority_tracker.escalateUrgency()
            messages.success(request, "কেসের তথ্য সফলভাবে আপডেট করা হয়েছে।")
            return redirect('cases:case_detail', pk=case.pk)
    else:
        initial_loc = {}
        if case.location:
            initial_loc = {
                'address': case.location.address,
                'area': case.location.area,
                'thana': case.location.thana,
                'city': case.location.city,
                'latitude': case.location.latitude,
                'longitude': case.location.longitude,
            }
        form = CaseCreateForm(instance=case, initial=initial_loc)

    return render(request, 'cases/case_edit.html', {'form': form, 'case': case})


@login_required
def case_update_status(request, pk):
    """
    Updates the case status (Searching -> Sighted -> Found -> Reunited).
    If status is Found or Reunited, autoArchive() is triggered to protect privacy.
    """
    case = get_object_or_404(MissingPersonCase, pk=pk)
    is_admin = request.user.is_superuser or request.user.is_staff or request.user.role == 'ADMIN'
    
    if not is_admin:
        messages.error(request, "শুধুমাত্র সিস্টেম অ্যাডমিন কেসের স্ট্যাটাস পরিবর্তন করার অনুমতি রাখেন।")
        return redirect('cases:case_detail', pk=pk)

    if request.method == 'POST':
        new_status = request.POST.get('caseStatus')
        if new_status in dict(MissingPersonCase.STATUS_CHOICES):
            case.caseStatus = new_status
            if new_status in ['FOUND', 'REUNITED']:
                case.autoArchive()
                messages.success(request, f"কেসটি সফলভাবে সমাধান করা হয়েছে! উদ্ধার ব্যক্তির গোপনীয়তা রক্ষার্থে ছবি ও সংবেদনশীল তথ্য স্বয়ংক্রিয়ভাবে লুকানো হয়েছে।")
                
                # Notify reporter & officer
                Notification.objects.create(
                    recipient=case.reporter.user,
                    case=case,
                    notificationType='CASE_RESOLVED',
                    title=f"কেস #{case.caseID} সমাধান: {case.fullName} নিরাপদে উদ্ধার!",
                    message=f"আলহামদুলিল্লাহ! {case.fullName} নিরাপদে পরিবারের কাছে ফিরে এসেছেন।",
                    priorityLevel='STANDARD'
                )
            else:
                case.save()
                messages.info(request, f"কেসের স্ট্যাটাস সফলভাবে আপডেট করা হয়েছে: {case.get_caseStatus_display()}")

    return redirect('cases:case_detail', pk=pk)


@login_required
def case_delete(request, pk):
    """
    Allows the user who created the post (reporter) or an Admin to delete the case.
    """
    case = get_object_or_404(MissingPersonCase, pk=pk)
    
    is_owner = hasattr(request.user, 'reporter_profile') and case.reporter == request.user.reporter_profile
    is_admin = request.user.is_superuser or request.user.is_staff or getattr(request.user, 'role', '') == 'ADMIN'
    
    if not (is_owner or is_admin):
        messages.error(request, "এই পোস্টটি মুছে ফেলার অনুমতি আপনার নেই।")
        return redirect('cases:case_detail', pk=pk)
        
    if request.method == 'POST':
        case_name = case.fullName
        case_id = case.caseID
        loc = case.location
        case.delete()
        if loc and not loc.cases.exists() and not loc.sightings.exists():
            loc.delete()
            
        messages.success(request, f"কেস #{case_id} ({case_name})-এর পোস্টটি সফলভাবে মুছে ফেলা হয়েছে।")
        
        next_url = request.POST.get('next') or request.GET.get('next')
        if next_url:
            return redirect(next_url)
        if is_admin and not is_owner:
            return redirect('verification:admin_dashboard')
        return redirect('cases:my_cases')
        
    return render(request, 'cases/case_confirm_delete.html', {'case': case})


@login_required
def my_cases(request):
    """Shows all cases filed by current user"""
    reporter = getattr(request.user, 'reporter_profile', None)
    if not reporter:
        cases = MissingPersonCase.objects.none()
    else:
        cases = MissingPersonCase.objects.filter(reporter=reporter).order_by('-created_at')
    return render(request, 'cases/my_cases.html', {'cases': cases})
