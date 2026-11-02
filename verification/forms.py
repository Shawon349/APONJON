from django import forms
from .models import VerificationCheck

class VerifyCaseForm(forms.ModelForm):
    gdNumber = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-red-500 font-mono tracking-wider uppercase',
            'placeholder': 'e.g. GD-2026-DHAN-9841 (ঐচ্ছিক)'
        }),
        help_text="থানা সাধারণ ডায়েরি (GD) নম্বর (যদি থাকে)"
    )
    verifyStatus = forms.ChoiceField(
        choices=[
            ('APPROVED', 'অনুমোদন ও ভেরিফাই (Verified ব্যাজ প্রদর্শন ও এরিয়া অ্যালার্ট)'),
            ('UNDER_INVESTIGATION', 'প্রাথমিক তদন্তাধীন রাখুন (Under Inquiry)'),
            ('REJECTED', 'রিপোর্ট বাতিল করুন (ভুয়া / অনাকাঙ্ক্ষিত কেস)'),
        ],
        widget=forms.Select(attrs={'class': 'w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-red-500'})
    )
    policeRemarks = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-red-500',
            'rows': 3,
            'placeholder': 'Add notes on the verification, investigating sub-inspector name, or initial police action...'
        })
    )

    class Meta:
        model = VerificationCheck
        fields = ['gdNumber', 'verifyStatus', 'policeRemarks']
