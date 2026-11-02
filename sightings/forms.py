from django import forms
from django.utils import timezone
from .models import SightingTip

class SightingTipForm(forms.ModelForm):
    # Location fields
    area = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-red-500', 'placeholder': 'e.g. Near Dhanmondi Lake Bridge, Road 8'})
    )
    thana = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-red-500', 'placeholder': 'e.g. Dhanmondi'})
    )
    latitude = forms.FloatField(
        required=False,
        widget=forms.HiddenInput(attrs={'id': 'id_tip_latitude'})
    )
    longitude = forms.FloatField(
        required=False,
        widget=forms.HiddenInput(attrs={'id': 'id_tip_longitude'})
    )

    sightingTime = forms.DateTimeField(
        label="আনুমানিক দেখার সময়",
        required=False,
        input_formats=[
            '%Y-%m-%dT%H:%M:%S',
            '%Y-%m-%dT%H:%M',
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%d %H:%M',
            '%m/%d/%Y %I:%M:%S %p',
            '%m/%d/%Y %I:%M %p',
            '%d/%m/%Y %I:%M:%S %p',
            '%d/%m/%Y %I:%M %p',
            '%m/%d/%Y %H:%M:%S',
            '%m/%d/%Y %H:%M',
            '%d/%m/%Y %H:%M:%S',
            '%d/%m/%Y %H:%M',
            '%Y-%m-%d',
            '%d/%m/%Y',
            '%m/%d/%Y',
        ],
        widget=forms.DateTimeInput(attrs={
            'class': 'w-full px-4 py-2.5 border border-gray-300 rounded-xl focus:ring-2 focus:ring-red-500 text-sm',
            'type': 'datetime-local',
            'id': 'id_sightingTime'
        })
    )

    class Meta:
        model = SightingTip
        fields = ['tipster_name', 'tipster_phone', 'sightingDescription', 'sightingTime', 'photoProof', 'photoURL']
        widgets = {
            'tipster_name': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-red-500', 'placeholder': 'Your Name (optional for anonymous)'}),
            'tipster_phone': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-red-500', 'placeholder': 'Contact Phone (for urgent police follow-up)'}),
            'sightingDescription': forms.Textarea(attrs={'class': 'w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-red-500', 'rows': 3, 'placeholder': 'Describe what you saw: clothing, physical condition, was someone accompanying them, direction they headed...'}),
            'photoProof': forms.FileInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-red-500'}),
            'photoURL': forms.URLInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-red-500', 'placeholder': 'Optional image link'}),
        }

    def clean_sightingTime(self):
        val = self.cleaned_data.get('sightingTime')
        if not val:
            return timezone.now()
        if timezone.is_naive(val):
            return timezone.make_aware(val, timezone.get_current_timezone())
        return val
