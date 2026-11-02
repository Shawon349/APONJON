from django import forms
from .models import MissingPersonCase

class CaseCreateForm(forms.ModelForm):
    # Location fields directly on the form for easy fast reporting
    address = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-red-500', 'placeholder': 'Last known street, house, or marketplace'})
    )
    area = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-red-500', 'placeholder': 'Neighborhood / Area e.g. Dhanmondi 27'})
    )
    thana = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-red-500', 'placeholder': 'Thana e.g. Dhanmondi, Mirpur'})
    )
    city = forms.CharField(
        initial="Dhaka",
        widget=forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-red-500'})
    )
    latitude = forms.FloatField(
        initial=23.7500,
        widget=forms.NumberInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg', 'step': '0.0001', 'id': 'id_latitude'})
    )
    longitude = forms.FloatField(
        initial=90.3800,
        widget=forms.NumberInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg', 'step': '0.0001', 'id': 'id_longitude'})
    )

    lastSeenTime = forms.DateTimeField(
        label="সর্বশেষ দেখার তারিখ ও সময়",
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
            'class': 'w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-red-500',
            'type': 'datetime-local',
            'id': 'id_lastSeenTime'
        })
    )

    class Meta:
        model = MissingPersonCase
        fields = [
            'fullName', 'age', 'gender', 'photo', 'photoURL',
            'lastSeenTime', 'clothingDetails', 'medicalConditions',
            'identifyingMarks', 'height'
        ]
        widgets = {
            'fullName': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-red-500', 'placeholder': 'Full Name'}),
            'age': forms.NumberInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-red-500', 'placeholder': 'Age'}),
            'gender': forms.Select(attrs={'class': 'w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-red-500'}),
            'photo': forms.FileInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-red-500'}),
            'photoURL': forms.URLInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-red-500', 'placeholder': 'Optional external photo URL'}),
            'clothingDetails': forms.Textarea(attrs={'class': 'w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-red-500', 'rows': 2, 'placeholder': 'Color of shirt, trousers, shoes, or any accessories...'}),
            'medicalConditions': forms.Textarea(attrs={'class': 'w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-red-500', 'rows': 2, 'placeholder': "e.g., Alzheimer's, Dementia, Autism, Diabetes, Speech impaired..."}),
            'identifyingMarks': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-red-500', 'placeholder': 'Scars, birthmarks, eyeglasses, etc.'}),
            'height': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-red-500', 'placeholder': "e.g., 5' 6\""}),
        }

    def clean_lastSeenTime(self):
        from django.utils import timezone
        val = self.cleaned_data.get('lastSeenTime')
        if not val:
            return timezone.now()
        if timezone.is_naive(val):
            return timezone.make_aware(val, timezone.get_current_timezone())
        return val


class CaseStatusUpdateForm(forms.ModelForm):
    class Meta:
        model = MissingPersonCase
        fields = ['caseStatus']
        widgets = {
            'caseStatus': forms.Select(attrs={'class': 'w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-red-500'}),
        }
