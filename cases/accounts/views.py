from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import User, PoliceOfficer, Reporter
from locations.models import Location
from .forms import (
    UserLoginForm, 
    ReporterRegistrationForm, 
    VolunteerRegistrationForm,
    OfficerRegistrationForm,
    PasswordResetDirectForm,
    UserPasswordChangeForm
)

def user_login(request):
    """Public login for Citizens and Family Reporters"""
    if request.user.is_authenticated:
        if request.user.role == 'ADMIN' or request.user.is_superuser:
            return redirect('verification:admin_dashboard')
        if request.user.role == 'POLICE' or hasattr(request.user, 'police_profile'):
            return redirect('accounts:officer_dashboard')
        return redirect('home')
        
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"স্বাগতম, {user.first_name or user.username}! আপনি সফলভাবে লগইন করেছেন।")
            if user.role == 'ADMIN' or user.is_superuser or user.is_staff:
                return redirect('verification:admin_dashboard')
            if user.role == 'POLICE' or hasattr(user, 'police_profile'):
                return redirect('accounts:officer_dashboard')
            return redirect('home')
        else:
            messages.error(request, "লগইন ব্যর্থ হয়েছে। অনুগ্রহ করে সঠিক ইউজারনেম এবং পাসওয়ার্ড দিন।")
    else:
        form = UserLoginForm()
    return render(request, 'accounts/login.html', {'form': form})


def admin_login(request):
    """
    Dedicated Private Admin Portal Login.
    Hidden from normal users.
    Default Admin: Sumsodduha / 47K3RWJ6
    """
    if request.user.is_authenticated and (request.user.role == 'ADMIN' or request.user.is_superuser):
        return redirect('verification:admin_dashboard')

    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            user = form.get_user()
            if not (user.role == 'ADMIN' or user.is_superuser or user.is_staff):
                messages.error(request, "প্রবেশাধিকার সংরক্ষিত। শুধুমাত্র অনুমোদিত অ্যাডমিন এখানে প্রবেশ করতে পারবেন।")
                return render(request, 'accounts/admin_login.html', {'form': form})

            login(request, user)
            messages.success(request, f"স্বাগতম অ্যাডমিন {user.get_full_name() or user.username}!")
            return redirect('verification:admin_dashboard')
        else:
            messages.error(request, "অ্যাডমিন ইউজারনেম বা পাসওয়ার্ড সঠিক নয়।")
    else:
        form = UserLoginForm()

    return render(request, 'accounts/admin_login.html', {'form': form})


def user_logout(request):
    logout(request)
    messages.info(request, "আপনি সফলভাবে লগআউট করেছেন।")
    return redirect('home')


def register_reporter(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = ReporterRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.role = 'REPORTER'
            user.save()

            # Create Location with user's full address
            location = Location.objects.create(
                address=form.cleaned_data.get('address', ''),
                area=form.cleaned_data.get('area', ''),
                thana=form.cleaned_data.get('thana', ''),
                city=form.cleaned_data.get('city', 'ঢাকা'),
                latitude=23.7500,
                longitude=90.3800
            )

            # Create Reporter Profile
            Reporter.createProfile(
                user=user,
                location=location,
                reporterType=form.cleaned_data.get('reporterType', 'Family Member'),
                relation=form.cleaned_data.get('relation', ''),
                nidNumber=form.cleaned_data.get('nidNumber', ''),
                isVerified=True
            )

            login(request, user)
            messages.success(request, "আপনার অ্যাকাউন্ট সফলভাবে তৈরি হয়েছে! আপনি এখন নিখোঁজ ব্যক্তির রিপোর্ট করতে পারবেন।")
            return redirect('cases:case_create')
        else:
            messages.error(request, "অনুগ্রহ করে ফর্মের ভুলগুলো সংশোধন করুন।")
    else:
        form = ReporterRegistrationForm()

    return render(request, 'accounts/register_reporter.html', {'form': form})


def register_volunteer(request):
    """
    Dedicated Volunteer Registration View.
    Enables community citizens to join search and rescue alert network.
    """
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = VolunteerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.role = 'CITIZEN'
            user.save()

            # Create Location with volunteer's coverage area
            location = Location.objects.create(
                address=f"{form.cleaned_data.get('area', '')}, {form.cleaned_data.get('thana', '')}",
                area=form.cleaned_data.get('area', ''),
                thana=form.cleaned_data.get('thana', ''),
                city=form.cleaned_data.get('city', 'ঢাকা'),
                latitude=23.7500,
                longitude=90.3800
            )

            # Create Reporter profile as Community Volunteer
            Reporter.createProfile(
                user=user,
                location=location,
                reporterType='Community Volunteer',
                relation=form.cleaned_data.get('volunteerSkill', 'Volunteer Field Support'),
                nidNumber=form.cleaned_data.get('nidNumber', ''),
                isVerified=True
            )

            login(request, user)
            messages.success(request, f"স্বাগতম {user.first_name or user.username}! আপনি আপনজন নেটওয়ার্কে একজন সম্মানিত স্বেচ্ছাসেবী হিসেবে যুক্ত হয়েছেন। নিখোঁজ ব্যক্তিদের পরিবারে ফিরিয়ে দিতে আপনার অবদান অত্যন্ত মূল্যবান।")
            return redirect('cases:case_list')
        else:
            messages.error(request, "অনুগ্রহ করে ফর্মের ভুলগুলো সংশোধন করুন।")
    else:
        form = VolunteerRegistrationForm()

    return render(request, 'accounts/register_volunteer.html', {'form': form})


def register_officer(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = OfficerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.role = 'POLICE'
            user.is_staff = True
            user.save()

            # Create Station Location
            location = Location.objects.create(
                address=form.cleaned_data.get('stationName', ''),
                area=form.cleaned_data.get('area', ''),
                thana=form.cleaned_data.get('thana', ''),
                city=form.cleaned_data.get('city', 'ঢাকা'),
                latitude=23.7500,
                longitude=90.3800
            )

            # Create Officer Profile
            PoliceOfficer.createProfile(
                user=user,
                badgeNumber=form.cleaned_data.get('badgeNumber'),
                stationName=form.cleaned_data.get('stationName'),
                jurisdiction=form.cleaned_data.get('jurisdiction'),
                location=location,
                isVerified=True
            )

            login(request, user)
            messages.success(request, "বাংলাদেশ পুলিশ অফিসার পোর্টাল অ্যাকাউন্ট সফলভাবে তৈরি হয়েছে!")
            return redirect('accounts:officer_dashboard')
        else:
            messages.error(request, "ফর্মের তথ্যগুলো সঠিক নয়। অনুগ্রহ করে পরীক্ষা করুন।")
    else:
        form = OfficerRegistrationForm()

    return render(request, 'accounts/register_officer.html', {'form': form})


def register_admin(request):
    """
    Dedicated Admin Registration View.
    Allows new admins to register with name, email, phone number, and password.
    """
    if request.user.is_authenticated and not request.user.is_superuser:
        return redirect('home')

    if request.method == 'POST':
        form = AdminRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.role = 'ADMIN'
            user.is_staff = True
            user.is_superuser = True
            user.save()

            login(request, user)
            messages.success(request, f"স্বাগতম অ্যাডমিন {user.get_full_name() or user.username}! আপনার অ্যাডমিনিস্ট্রেটর অ্যাকাউন্ট সফলভাবে তৈরি হয়েছে।")
            return redirect('verification:admin_dashboard')
        else:
            messages.error(request, "ফর্মের তথ্যগুলোতে ভুল রয়েছে। অনুগ্রহ করে সংশোধন করুন।")
    else:
        form = AdminRegistrationForm()

    return render(request, 'accounts/register_admin.html', {'form': form})


from django.core.mail import send_mail
from .models import PasswordResetCode
from .forms import PasswordResetEmailRequestForm, PasswordResetVerifyCodeForm

def reset_password_request(request):
    """
    Step 1: User or Admin enters email.
    A 6-digit verification code is generated and sent to their email.
    """
    if request.method == 'POST':
        form = PasswordResetEmailRequestForm(request.POST)
        if form.is_valid():
            user = form.matched_user
            # Invalidate previous unused codes
            PasswordResetCode.objects.filter(user=user, is_used=False).update(is_used=True)
            
            # Generate new 6-digit code
            code_obj = PasswordResetCode.create_for_user(user)

            # Send verification email
            subject = "আপনজন - পাসওয়ার্ড রিসেট ভেরিফিকেশন কোড"
            message = (
                f"আসসালামু আলাইকুম {user.first_name or user.username},\n\n"
                f"আপনজন প্ল্যাটফর্মে আপনার পাসওয়ার্ড রিসেট করার জন্য ৬-ডিজিটের ভেরিফিকেশন কোড:\n\n"
                f"👉  {code_obj.code}  👈\n\n"
                f"এই কোডটির মেয়াদ ১৫ মিনিট। আপনি যদি এই অনুরোধ না করে থাকেন, তবে অনুগ্রহ করে এটি উপেক্ষা করুন।\n\n"
                f"— টিম আপনজন"
            )
            try:
                send_mail(subject, message, 'support@aponjon.org', [user.email], fail_silently=True)
            except Exception:
                pass

            # Store user ID and generated code in session for Step 2
            request.session['reset_user_id'] = user.pk
            request.session['reset_code_display'] = code_obj.code
            
            messages.success(request, f"আপনার ভেরিফিকেশন কোডটি প্রস্তুত করা হয়েছে! [নিরাপত্তা কোড: {code_obj.code}]")
            return redirect('accounts:reset_password_verify')
        else:
            messages.error(request, "প্রদত্ত তথ্য দিয়ে কোনো অ্যাকাউন্ট খুঁজে পাওয়া যায়নি।")
    else:
        form = PasswordResetEmailRequestForm()

    return render(request, 'accounts/reset_password_request.html', {'form': form})


def reset_password_verify(request):
    """
    Step 2: User enters the 6-digit verification code and sets a new password.
    Code is prominently displayed for PythonAnywhere free hosting compatibility.
    """
    user_id = request.session.get('reset_user_id')
    display_code = request.session.get('reset_code_display')
    if not user_id:
        messages.warning(request, "অনুগ্রহ করে প্রথমে আপনার তথ্য প্রদান করুন।")
        return redirect('accounts:reset_password')

    user = get_object_or_404(User, pk=user_id)

    if request.method == 'POST':
        form = PasswordResetVerifyCodeForm(user, request.POST)
        if form.is_valid():
            new_password = form.cleaned_data['new_password']
            user.set_password(new_password)
            user.save()

            # Mark code as used
            form.valid_code_obj.is_used = True
            form.valid_code_obj.save()

            # Clear session
            if 'reset_user_id' in request.session:
                del request.session['reset_user_id']
            if 'reset_code_display' in request.session:
                del request.session['reset_code_display']

            messages.success(request, "আপনার পাসওয়ার্ড সফলভাবে রিসেট করা হয়েছে! নতুন পাসওয়ার্ড দিয়ে লগইন করুন।")
            return redirect('accounts:login')
        else:
            messages.error(request, "ভেরিফিকেশন কোডটি সঠিক নয় বা পাসওয়ার্ডের নিয়মে ভুল রয়েছে।")
    else:
        initial_data = {}
        if display_code:
            initial_data['code'] = display_code
        form = PasswordResetVerifyCodeForm(user, initial=initial_data)

    return render(request, 'accounts/reset_password_verify.html', {
        'form': form, 
        'user_email': user.email or user.phone or user.username,
        'display_code': display_code
    })


@login_required
def change_password(request):
    """Allows logged-in users to update or change their password"""
    if request.method == 'POST':
        form = UserPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            new_password = form.cleaned_data['new_password']
            request.user.set_password(new_password)
            request.user.save()
            update_session_auth_hash(request, request.user) # Keeps user logged in
            messages.success(request, "আপনার পাসওয়ার্ড সফলভাবে আপডেট করা হয়েছে!")
            return redirect('accounts:profile')
        else:
            messages.error(request, "পাসওয়ার্ড পরিবর্তনে সমস্যা হয়েছে। সঠিক তথ্য প্রদান করুন।")
    else:
        form = UserPasswordChangeForm(request.user)

    return render(request, 'accounts/change_password.html', {'form': form})


@login_required
def profile_view(request):
    user = request.user

    if request.method == 'POST' and 'profile_picture' in request.FILES:
        pic = request.FILES['profile_picture']
        try:
            user.profilePicture = pic
            user.save()
            messages.success(request, "আপনার প্রোফাইল ছবি সফলভাবে আপডেট করা হয়েছে!")
        except Exception:
            messages.error(request, "ছবি আপলোড করতে সমস্যা হয়েছে। অনুগ্রহ করে ছবি নির্বাচন করে পুনরায় চেষ্টা করুন।")
        return redirect('accounts:profile')

    officer_profile = getattr(user, 'police_profile', None)
    reporter_profile = getattr(user, 'reporter_profile', None)

    context = {
        'user': user,
        'officer_profile': officer_profile,
        'reporter_profile': reporter_profile,
    }
    return render(request, 'accounts/profile.html', context)


@login_required
def officer_dashboard(request):
    if not (request.user.role == 'POLICE' or hasattr(request.user, 'police_profile') or request.user.is_superuser):
        messages.error(request, "এই পেজে প্রবেশের জন্য পুলিশ অফিসারের অনুমতি প্রয়োজন।")
        return redirect('home')

    from cases.models import MissingPersonCase
    from sightings.models import SightingTip

    pending_verifications = MissingPersonCase.objects.filter(verification__verifyStatus='PENDING').order_by('-created_at')
    active_cases = MissingPersonCase.objects.filter(caseStatus__in=['SEARCHING', 'SIGHTED']).order_by('-created_at')
    recent_tips = SightingTip.objects.filter(status='PENDING').order_by('-sightingTime')
    resolved_cases = MissingPersonCase.objects.filter(caseStatus__in=['FOUND', 'REUNITED']).order_by('-updated_at')[:5]

    context = {
        'pending_verifications': pending_verifications,
        'active_cases': active_cases,
        'recent_tips': recent_tips,
        'resolved_cases': resolved_cases,
    }
    return render(request, 'accounts/officer_dashboard.html', context)
