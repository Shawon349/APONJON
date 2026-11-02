from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import SightingTip
from .forms import SightingTipForm
from cases.models import MissingPersonCase
from locations.models import Location
from accounts.models import Reporter

def submit_tip(request, case_id):
    """Allows anyone (public/volunteer/citizen) to submit a sighting tip"""
    case = get_object_or_404(MissingPersonCase, pk=case_id)

    if request.method == 'POST':
        form = SightingTipForm(request.POST, request.FILES)
        if form.is_valid():
            # Create sighting location
            lat = form.cleaned_data.get('latitude') or (case.location.latitude if case.location else 23.7500)
            lon = form.cleaned_data.get('longitude') or (case.location.longitude if case.location else 90.3800)
            
            location = Location.objects.create(
                address=form.cleaned_data['area'],
                area=form.cleaned_data['area'],
                thana=form.cleaned_data['thana'],
                city="Dhaka",
                latitude=lat,
                longitude=lon
            )

            reporter = None
            if request.user.is_authenticated and hasattr(request.user, 'reporter_profile'):
                reporter = request.user.reporter_profile

            tip = SightingTip.createTip(
                case=case,
                sightingDescription=form.cleaned_data['sightingDescription'],
                sightingTime=form.cleaned_data['sightingTime'],
                location=location,
                reporter=reporter,
                photoProof=form.cleaned_data.get('photoProof'),
                tipster_name=form.cleaned_data.get('tipster_name', ''),
                tipster_phone=form.cleaned_data.get('tipster_phone', '')
            )
            if form.cleaned_data.get('photoURL'):
                tip.photoURL = form.cleaned_data['photoURL']
                tip.save()

            messages.success(request, "ধন্যবাদ! আপনার দেওয়া তথ্যটি গৃহীত হয়েছে এবং তাৎক্ষণিকভাবে পুলিশ ও পরিবারকে অবহিত করা হয়েছে।")
            return redirect('cases:case_detail', pk=case.caseID)
    else:
        form = SightingTipForm()

    return render(request, 'sightings/submit_tip.html', {'form': form, 'case': case})


@login_required
def flag_tip_credible(request, tip_id):
    """Police officer or Case owner marks tip as credible"""
    tip = get_object_or_404(SightingTip, pk=tip_id)
    case = tip.case

    is_owner = hasattr(request.user, 'reporter_profile') and case.reporter == request.user.reporter_profile
    is_officer = request.user.role == 'POLICE' or hasattr(request.user, 'police_profile') or request.user.is_staff or request.user.is_superuser
    
    if not (is_owner or is_officer):
        messages.error(request, "অনুমতি নেই।")
        return redirect('cases:case_detail', pk=case.caseID)

    tip.flagCredible()
    messages.success(request, f"ক্লু #{tip.tipID} নির্ভরযোগ্য হিসেবে চিহ্নিত করা হয়েছে। কেসের স্ট্যাটাস 'তথ্য পাওয়া গেছে'-তে হালনাগাদ হয়েছে।")
    return redirect('cases:case_detail', pk=case.caseID)


@login_required
def dismiss_tip(request, tip_id):
    """Marks tip as dismissed/false lead"""
    tip = get_object_or_404(SightingTip, pk=tip_id)
    case = tip.case

    is_owner = hasattr(request.user, 'reporter_profile') and case.reporter == request.user.reporter_profile
    is_officer = request.user.role == 'POLICE' or hasattr(request.user, 'police_profile') or request.user.is_staff or request.user.is_superuser
    
    if not (is_owner or is_officer):
        messages.error(request, "অনুমতি নেই।")
        return redirect('cases:case_detail', pk=case.caseID)

    tip.cancelTip()
    messages.info(request, f"ক্লু #{tip.tipID} বাতিল করা হয়েছে।")
    return redirect('cases:case_detail', pk=case.caseID)
