from django import forms
from django.db import models
from django.contrib.auth import authenticate
from .models import User, PoliceOfficer, Reporter
from locations.models import Location

class UserLoginForm(forms.Form):
    username_or_email = forms.CharField(
        label="ইউজারনেম অথবা ইমেইল",
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 rounded-xl border border-gray-300 focus:ring-2 focus:ring-red-500 focus:outline-none transition text-sm',
            'placeholder': 'ইউজারনেম অথবা ইমেইল লিখুন'
        })
    )
    password = forms.CharField(
        label="পাসওয়ার্ড",
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-3 rounded-xl border border-gray-300 focus:ring-2 focus:ring-red-500 focus:outline-none transition text-sm',
            'placeholder': 'আপনার পাসওয়ার্ড লিখুন'
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        username_or_email = cleaned_data.get('username_or_email')
        password = cleaned_data.get('password')

        if username_or_email and password:
            clean_username = username_or_email.strip()

            # Check if input is email or username
            user = None
            if '@' in clean_username:
                try:
                    user_obj = User.objects.get(email__iexact=clean_username)
                    user = authenticate(username=user_obj.username, password=password)
                except User.DoesNotExist:
                    user = None
            else:
                user = authenticate(username=clean_username, password=password)

            if not user:
                raise forms.ValidationError("ইউজারনেম অথবা পাসওয়ার্ড সঠিক নয়। অনুগ্রহ করে পুনরায় চেষ্টা করুন।")
            self.user_cache = user
        return cleaned_data

    def get_user(self):
        return getattr(self, 'user_cache', None)


class ReporterRegistrationForm(forms.ModelForm):
    first_name = forms.CharField(
        label="প্রথম নাম",
        required=True,
        widget=forms.TextInput(attrs={'class': 'w-full px-4 py-2.5 border border-gray-300 rounded-xl focus:ring-2 focus:ring-red-500 text-sm', 'placeholder': 'আপনার প্রথম নাম লিখুন'})
    )
    last_name = forms.CharField(
        label="শেষ নাম",
        required=True,
        widget=forms.TextInput(attrs={'class': 'w-full px-4 py-2.5 border border-gray-300 rounded-xl focus:ring-2 focus:ring-red-500 text-sm', 'placeholder': 'আপনার শেষ নাম লিখুন'})
    )
    email = forms.EmailField(
        label="বৈধ ইমেইল ঠিকানা *",
        required=True,
        widget=forms.EmailInput(attrs={'class': 'w-full px-4 py-2.5 border border-gray-300 rounded-xl focus:ring-2 focus:ring-red-500 text-sm', 'placeholder': 'valid_email@example.com'})
    )
    phone = forms.CharField(
        label="মোবাইল নম্বর *",
        required=True,
        widget=forms.TextInput(attrs={'class': 'w-full px-4 py-2.5 border border-gray-300 rounded-xl focus:ring-2 focus:ring-red-500 text-sm', 'placeholder': '০১৭১১-XXXXXX'})
    )
    
    # Address details as explicitly requested
    address = forms.CharField(
        label="পূর্ণ ঠিকানা (বাড়ি/রোড/ব্লক) *",
        required=True,
        widget=forms.TextInput(attrs={'class': 'w-full px-4 py-2.5 border border-gray-300 rounded-xl focus:ring-2 focus:ring-red-500 text-sm', 'placeholder': 'উদা: বাসা ১২, রোড ৪, ব্লক সি'})
    )
    area = forms.CharField(
        label="মহল্লা / এলাকা *",
        required=True,
        widget=forms.TextInput(attrs={'class': 'w-full px-4 py-2.5 border border-gray-300 rounded-xl focus:ring-2 focus:ring-red-500 text-sm', 'placeholder': 'উদা: ধানমন্ডি ২৭'})
    )
    thana = forms.CharField(
        label="থানা *",
        required=True,
        widget=forms.TextInput(attrs={'class': 'w-full px-4 py-2.5 border border-gray-300 rounded-xl focus:ring-2 focus:ring-red-500 text-sm', 'placeholder': 'উদা: ধানমন্ডি থানা'})
    )
    city = forms.CharField(
        label="জেলা / শহর",
        initial="ঢাকা",
        required=True,
        widget=forms.TextInput(attrs={'class': 'w-full px-4 py-2.5 border border-gray-300 rounded-xl focus:ring-2 focus:ring-red-500 text-sm', 'placeholder': 'উদা: ঢাকা'})
    )

    reporterType = forms.ChoiceField(
        label="ব্যবহারকারীর ধরন",
        choices=[
            ('Family Member', 'পরিবারের সদস্য (Family Member)'),
            ('Relative', 'আত্মীয়স্বজন (Relative)'),
            ('Legal Guardian', 'আইনি অভিভাবক (Legal Guardian)'),
            ('Concerned Citizen', 'সচেতন নাগরিক (Citizen)'),
            ('Community Volunteer', 'স্বেচ্ছাসেবক (Volunteer)'),
        ],
        widget=forms.Select(attrs={'class': 'w-full px-4 py-2.5 border border-gray-300 rounded-xl focus:ring-2 focus:ring-red-500 text-sm'})
    )
    relation = forms.CharField(
        label="নিখোঁজ ব্যক্তির সাথে সম্পর্ক",
        required=False,
        widget=forms.TextInput(attrs={'class': 'w-full px-4 py-2.5 border border-gray-300 rounded-xl focus:ring-2 focus:ring-red-500 text-sm', 'placeholder': 'উদা: ভাই, বোন, পিতা, মাতা, সন্তান'})
    )
    nidNumber = forms.CharField(
        label="জাতীয় পরিচয়পত্র (NID) নম্বর",
        required=False,
        widget=forms.TextInput(attrs={'class': 'w-full px-4 py-2.5 border border-gray-300 rounded-xl focus:ring-2 focus:ring-red-500 text-sm', 'placeholder': '১০ বা ১৭ ডিজিটের এনআইডি'})
    )

    password = forms.CharField(
        label="পাসওয়ার্ড (কমপক্ষে ৬ অক্ষর) *",
        widget=forms.PasswordInput(attrs={'class': 'w-full px-4 py-2.5 border border-gray-300 rounded-xl focus:ring-2 focus:ring-red-500 text-sm', 'placeholder': 'কমপক্ষে ৬ অক্ষরের পাসওয়ার্ড'})
    )
    confirm_password = forms.CharField(
        label="পাসওয়ার্ড নিশ্চিত করুন *",
        widget=forms.PasswordInput(attrs={'class': 'w-full px-4 py-2.5 border border-gray-300 rounded-xl focus:ring-2 focus:ring-red-500 text-sm', 'placeholder': 'একই পাসওয়ার্ড পুনরায় লিখুন'})
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'phone']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'w-full px-4 py-2.5 border border-gray-300 rounded-xl focus:ring-2 focus:ring-red-500 text-sm', 'placeholder': 'ইউজারনেম (উদা: citizen2026)'}),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()
        if not email:
            raise forms.ValidationError("একটি কার্যকর ইমেইল ঠিকানা প্রদান করা বাধ্যতামূলক।")

        from django.core.validators import validate_email
        try:
            validate_email(email)
        except forms.ValidationError:
            raise forms.ValidationError("অনুগ্রহ করে একটি সঠিক ও বৈধ ইমেইল ঠিকানা লিখুন (যেমন: name@example.com)।")

        parts = email.split('@')
        if len(parts) != 2 or '.' not in parts[1] or len(parts[1].split('.')[-1]) < 2:
            raise forms.ValidationError("ইমেইলের ডোমেইন সঠিক নয়। অনুগ্রহ করে একটি বৈধ ইমেইল দিন (যেমন: gmail.com, yahoo.com, outlook.com)।")

        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("এই ইমেইল দিয়ে ইতিমধ্যে একটি অ্যাকাউন্ট নিবন্ধিত আছে। অনুগ্রহ করে এই ইমেইল দিয়ে সরাসরি লগইন করুন।")
        return email

    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name', '').strip()
        if not first_name:
            raise forms.ValidationError("আপনার নাম প্রদান করা বাধ্যতামূলক।")
        return first_name

    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '').strip()
        digits = ''.join(filter(str.isdigit, phone))
        if not phone or len(digits) < 11:
            raise forms.ValidationError("একটি সঠিক ১১ ডিজিটের মোবাইল নম্বর প্রদান করা বাধ্যতামূলক (যেমন: 01711234567)।")
        return phone

    def clean_username(self):
        username = self.cleaned_data.get('username', '').strip()
        if len(username) < 3:
            raise forms.ValidationError("ইউজারনেম কমপক্ষে ৩ অক্ষরের হতে হবে।")
        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError("এই ইউজারনেমটি ইতিমধ্যে ব্যবহৃত হয়েছে। অনুগ্রহ করে অন্য একটি ইউজারনেম দিন।")
        return username

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('password')
        p2 = cleaned_data.get('confirm_password')
        if p1 and len(p1) < 6:
            self.add_error('password', 'পাসওয়ার্ড সুরক্ষার জন্য কমপক্ষে ৬ অক্ষরের হতে হবে।')
        if p1 and p2 and p1 != p2:
            self.add_error('confirm_password', 'উভয় পাসওয়ার্ড হুবহু মিলছে না।')
        return cleaned_data


class VolunteerRegistrationForm(forms.ModelForm):
    first_name = forms.CharField(
        label="প্রথম নাম *",
        required=True,
        widget=forms.TextInput(attrs={'class': 'w-full px-4 py-2.5 border border-gray-300 rounded-xl focus:ring-2 focus:ring-emerald-500 text-sm', 'placeholder': 'আপনার প্রথম নাম'})
    )
    last_name = forms.CharField(
        label="শেষ নাম *",
        required=True,
        widget=forms.TextInput(attrs={'class': 'w-full px-4 py-2.5 border border-gray-300 rounded-xl focus:ring-2 focus:ring-emerald-500 text-sm', 'placeholder': 'আপনার শেষ নাম'})
    )
    email = forms.EmailField(
        label="বৈধ ইমেইল ঠিকানা *",
        required=True,
        widget=forms.EmailInput(attrs={'class': 'w-full px-4 py-2.5 border border-gray-300 rounded-xl focus:ring-2 focus:ring-emerald-500 text-sm', 'placeholder': 'your_email@example.com'})
    )
    phone = forms.CharField(
        label="যোগাযোগের মোবাইল নম্বর *",
        required=True,
        widget=forms.TextInput(attrs={'class': 'w-full px-4 py-2.5 border border-gray-300 rounded-xl focus:ring-2 focus:ring-emerald-500 text-sm', 'placeholder': '০১৭১১-XXXXXX'})
    )
    area = forms.CharField(
        label="আপনার এলাকা / মহল্লা *",
        required=True,
        widget=forms.TextInput(attrs={'class': 'w-full px-4 py-2.5 border border-gray-300 rounded-xl focus:ring-2 focus:ring-emerald-500 text-sm', 'placeholder': 'উদা: মিরপুর ১০'})
    )
    thana = forms.CharField(
        label="থানা এলাকা *",
        required=True,
        widget=forms.TextInput(attrs={'class': 'w-full px-4 py-2.5 border border-gray-300 rounded-xl focus:ring-2 focus:ring-emerald-500 text-sm', 'placeholder': 'উদা: মিরপুর'})
    )
    city = forms.CharField(
        label="জেলা / শহর",
        initial="ঢাকা",
        required=True,
        widget=forms.TextInput(attrs={'class': 'w-full px-4 py-2.5 border border-gray-300 rounded-xl focus:ring-2 focus:ring-emerald-500 text-sm', 'placeholder': 'উদা: ঢাকা'})
    )
    volunteerSkill = forms.ChoiceField(
        label="কীভাবে সাহায্য করতে চান? *",
        choices=[
            ('Field Search', 'মাঠপর্যায়ে তল্লাশি ও উদ্ধার অভিযান (Field Search & Rescue)'),
            ('Information Clues', 'এলাকায় নিখোঁজ ব্যক্তিদের প্রত্যক্ষদর্শী তথ্য ও ক্লু প্রদান'),
            ('Social Media Alert', 'সামাজিক মাধ্যম ও এলাকায় নোটিশ/পোস্টার প্রচার'),
            ('Transport Support', 'জরুরী পরিবহন ও বাইক/গাড়ি সহায়তা (Transport Assistance)'),
            ('Medical & Counseling', 'প্রাথমিক চিকিৎসা বা পরিবারকে মানসিক সমর্থন (First Aid & Counseling)'),
        ],
        widget=forms.Select(attrs={'class': 'w-full px-4 py-2.5 border border-gray-300 rounded-xl focus:ring-2 focus:ring-emerald-500 text-sm'})
    )
    nidNumber = forms.CharField(
        label="জাতীয় পরিচয়পত্র (NID) নম্বর (ঐচ্ছিক)",
        required=False,
        widget=forms.TextInput(attrs={'class': 'w-full px-4 py-2.5 border border-gray-300 rounded-xl focus:ring-2 focus:ring-emerald-500 text-sm', 'placeholder': '১০ বা ১৭ ডিজিটের এনআইডি'})
    )
    password = forms.CharField(
        label="পাসওয়ার্ড (কমপক্ষে ৬ অক্ষর) *",
        widget=forms.PasswordInput(attrs={'class': 'w-full px-4 py-2.5 border border-gray-300 rounded-xl focus:ring-2 focus:ring-emerald-500 text-sm', 'placeholder': 'কমপক্ষে ৬ অক্ষরের পাসওয়ার্ড'})
    )
    confirm_password = forms.CharField(
        label="পাসওয়ার্ড নিশ্চিত করুন *",
        widget=forms.PasswordInput(attrs={'class': 'w-full px-4 py-2.5 border border-gray-300 rounded-xl focus:ring-2 focus:ring-emerald-500 text-sm', 'placeholder': 'একই পাসওয়ার্ড পুনরায় লিখুন'})
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'phone']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'w-full px-4 py-2.5 border border-gray-300 rounded-xl focus:ring-2 focus:ring-emerald-500 text-sm', 'placeholder': 'ইউজারনেম (উদা: volunteer_arif)'}),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()
        if not email:
            raise forms.ValidationError("একটি কার্যকর ইমেইল প্রদান বাধ্যতামূলক।")

        from django.core.validators import validate_email
        try:
            validate_email(email)
        except forms.ValidationError:
            raise forms.ValidationError("অনুগ্রহ করে একটি সঠিক ও বৈধ ইমেইল লিখুন।")

        parts = email.split('@')
        if len(parts) != 2 or '.' not in parts[1] or len(parts[1].split('.')[-1]) < 2:
            raise forms.ValidationError("ইমেইলের ডোমেইন সঠিক নয় (যেমন: gmail.com, yahoo.com)।")

        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("এই ইমেইল দিয়ে ইতিমধ্যে একটি অ্যাকাউন্ট নিবন্ধিত আছে। দয়া করে লগইন করুন।")
        return email

    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name', '').strip()
        if not first_name:
            raise forms.ValidationError("আপনার নাম প্রদান করা বাধ্যতামূলক।")
        return first_name

    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '').strip()
        digits = ''.join(filter(str.isdigit, phone))
        if not phone or len(digits) < 11:
            raise forms.ValidationError("একটি সঠিক ১১ ডিজিটের মোবাইল নম্বর প্রদান করা বাধ্যতামূলক (যেমন: 01711234567)।")
        return phone

    def clean_username(self):
        username = self.cleaned_data.get('username', '').strip()
        if len(username) < 3:
            raise forms.ValidationError("ইউজারনেম কমপক্ষে ৩ অক্ষরের হতে হবে।")
        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError("এই ইউজারনেমটি ইতিমধ্যে ব্যবহৃত হয়েছে।")
        return username

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('password')
        p2 = cleaned_data.get('confirm_password')
        if p1 and len(p1) < 6:
            self.add_error('password', 'পাসওয়ার্ড সুরক্ষার জন্য কমপক্ষে ৬ অক্ষরের হতে হবে।')
        if p1 and p2 and p1 != p2:
            self.add_error('confirm_password', 'উভয় পাসওয়ার্ড হুবহু মিলছে না।')
        return cleaned_data


class OfficerRegistrationForm(forms.ModelForm):
    first_name = forms.CharField(
        label="প্রথম নাম",
        required=True,
        widget=forms.TextInput(attrs={'class': 'w-full px-4 py-2.5 border border-gray-300 rounded-xl focus:ring-2 focus:ring-red-500 text-sm', 'placeholder': 'উদা: তানভীর'})
    )
    last_name = forms.CharField(
        label="শেষ নাম",
        required=True,
        widget=forms.TextInput(attrs={'class': 'w-full px-4 py-2.5 border border-gray-300 rounded-xl focus:ring-2 focus:ring-red-500 text-sm', 'placeholder': 'উদা: রহমান'})
    )
    email = forms.EmailField(
        label="দাপ্তরিক ইমেইল",
        required=True,
        widget=forms.EmailInput(attrs={'class': 'w-full px-4 py-2.5 border border-gray-300 rounded-xl focus:ring-2 focus:ring-red-500 text-sm', 'placeholder': 'officer@police.gov.bd'})
    )
    phone = forms.CharField(
        label="ডিউটি মোবাইল নম্বর",
        required=True,
        widget=forms.TextInput(attrs={'class': 'w-full px-4 py-2.5 border border-gray-300 rounded-xl focus:ring-2 focus:ring-red-500 text-sm', 'placeholder': '০১৭১১-XXXXXX'})
    )
    badgeNumber = forms.CharField(
        label="বিপি / ব্যাজ নম্বর",
        required=True,
        widget=forms.TextInput(attrs={'class': 'w-full px-4 py-2.5 border border-gray-300 rounded-xl focus:ring-2 focus:ring-red-500 text-sm', 'placeholder': 'BP-849102'})
    )
    stationName = forms.CharField(
        label="থানার নাম",
        required=True,
        widget=forms.TextInput(attrs={'class': 'w-full px-4 py-2.5 border border-gray-300 rounded-xl focus:ring-2 focus:ring-red-500 text-sm', 'placeholder': 'ধানমন্ডি মডেল থানা'})
    )
    jurisdiction = forms.CharField(
        label="আওতাধীন এলাকা",
        required=True,
        widget=forms.TextInput(attrs={'class': 'w-full px-4 py-2.5 border border-gray-300 rounded-xl focus:ring-2 focus:ring-red-500 text-sm', 'placeholder': 'ধানমন্ডি, কলাবাগান'})
    )
    area = forms.CharField(
        label="মহল্লা / এলাকা",
        required=True,
        widget=forms.TextInput(attrs={'class': 'w-full px-4 py-2.5 border border-gray-300 rounded-xl focus:ring-2 focus:ring-red-500 text-sm', 'placeholder': 'ধানমন্ডি'})
    )
    thana = forms.CharField(
        label="থানা",
        required=True,
        widget=forms.TextInput(attrs={'class': 'w-full px-4 py-2.5 border border-gray-300 rounded-xl focus:ring-2 focus:ring-red-500 text-sm', 'placeholder': 'ধানমন্ডি'})
    )
    city = forms.CharField(
        label="জেলা",
        initial="ঢাকা",
        required=True,
        widget=forms.TextInput(attrs={'class': 'w-full px-4 py-2.5 border border-gray-300 rounded-xl focus:ring-2 focus:ring-red-500 text-sm'})
    )

    password = forms.CharField(
        label="পাসওয়ার্ড",
        widget=forms.PasswordInput(attrs={'class': 'w-full px-4 py-2.5 border border-gray-300 rounded-xl focus:ring-2 focus:ring-red-500 text-sm', 'placeholder': 'সুরক্ষিত পাসওয়ার্ড দিন'})
    )
    confirm_password = forms.CharField(
        label="পাসওয়ার্ড নিশ্চিত করুন",
        widget=forms.PasswordInput(attrs={'class': 'w-full px-4 py-2.5 border border-gray-300 rounded-xl focus:ring-2 focus:ring-red-500 text-sm', 'placeholder': 'একই পাসওয়ার্ড পুনরায় লিখুন'})
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'phone']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'w-full px-4 py-2.5 border border-gray-300 rounded-xl focus:ring-2 focus:ring-red-500 text-sm', 'placeholder': 'অফিসার ইউজারনেম'}),
        }

    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name', '').strip()
        if not first_name:
            raise forms.ValidationError("অফিসারের নাম প্রদান করা বাধ্যতামূলক।")
        return first_name

    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '').strip()
        digits = ''.join(filter(str.isdigit, phone))
        if not phone or len(digits) < 11:
            raise forms.ValidationError("একটি সঠিক ১১ ডিজিটের ডিউটি মোবাইল নম্বর প্রদান করা বাধ্যতামূলক।")
        return phone

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('password')
        p2 = cleaned_data.get('confirm_password')
        if p1 and p2 and p1 != p2:
            self.add_error('confirm_password', 'উভয় পাসওয়ার্ড হুবহু মিলছে না।')
        return cleaned_data


class PasswordResetDirectForm(forms.Form):
    """
    Direct self-service password reset form.
    Allows user to verify username along with email or phone and set a new password.
    """
    identifier = forms.CharField(
        label="ইউজারনেম অথবা নিবন্ধিত ইমেইল",
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2.5 border border-gray-300 rounded-xl focus:ring-2 focus:ring-red-500 text-sm',
            'placeholder': 'আপনার ইউজারনেম বা ইমেইল লিখুন'
        })
    )
    phone_verification = forms.CharField(
        label="নিবন্ধিত মোবাইল নম্বর",
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2.5 border border-gray-300 rounded-xl focus:ring-2 focus:ring-red-500 text-sm',
            'placeholder': 'অ্যাকাউন্টে দেওয়া মোবাইল নম্বর'
        })
    )
    new_password = forms.CharField(
        label="নতুন পাসওয়ার্ড",
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-2.5 border border-gray-300 rounded-xl focus:ring-2 focus:ring-red-500 text-sm',
            'placeholder': 'নতুন পাসওয়ার্ড লিখুন (কমপক্ষে ৪ অক্ষর)'
        })
    )
    confirm_new_password = forms.CharField(
        label="নতুন পাসওয়ার্ড নিশ্চিত করুন",
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-2.5 border border-gray-300 rounded-xl focus:ring-2 focus:ring-red-500 text-sm',
            'placeholder': 'একই পাসওয়ার্ড পুনরায় লিখুন'
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        identifier = cleaned_data.get('identifier', '').strip()
        phone_verification = cleaned_data.get('phone_verification', '').strip()
        p1 = cleaned_data.get('new_password')
        p2 = cleaned_data.get('confirm_new_password')

        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("নতুন পাসওয়ার্ড দুটি মিলছে না।")

        if len(p1 or '') < 4:
            raise forms.ValidationError("পাসওয়ার্ড কমপক্ষে ৪ অক্ষরের হতে হবে।")

        # Find user
        user = User.objects.filter(models.Q(username__iexact=identifier) | models.Q(email__iexact=identifier)).first()
        if not user:
            raise forms.ValidationError("প্রদত্ত ইউজারনেম বা ইমেইল দিয়ে কোনো অ্যাকাউন্ট পাওয়া যায়নি।")

        # Check phone match
        clean_user_phone = ''.join(filter(str.isdigit, user.phone or ''))
        clean_input_phone = ''.join(filter(str.isdigit, phone_verification or ''))

        if clean_user_phone and clean_input_phone and (clean_input_phone not in clean_user_phone and clean_user_phone not in clean_input_phone):
            raise forms.ValidationError("নিবন্ধিত মোবাইল নম্বরের সাথে মিলছে না। অনুগ্রহ করে সঠিক নম্বর দিন।")

        self.matched_user = user
        return cleaned_data


class UserPasswordChangeForm(forms.Form):
    """Change password form for logged-in users"""
    current_password = forms.CharField(
        label="বর্তমান পাসওয়ার্ড",
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-2.5 border border-gray-300 rounded-xl focus:ring-2 focus:ring-red-500 text-sm',
            'placeholder': 'বর্তমান পাসওয়ার্ড লিখুন'
        })
    )
    new_password = forms.CharField(
        label="নতুন পাসওয়ার্ড",
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-2.5 border border-gray-300 rounded-xl focus:ring-2 focus:ring-red-500 text-sm',
            'placeholder': 'নতুন পাসওয়ার্ড লিখুন'
        })
    )
    confirm_new_password = forms.CharField(
        label="নতুন পাসওয়ার্ড নিশ্চিত করুন",
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-2.5 border border-gray-300 rounded-xl focus:ring-2 focus:ring-red-500 text-sm',
            'placeholder': 'একই পাসওয়ার্ড পুনরায় লিখুন'
        })
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_current_password(self):
        curr = self.cleaned_data.get('current_password')
        if not self.user.check_password(curr):
            raise forms.ValidationError("বর্তমান পাসওয়ার্ড সঠিক নয়।")
        return curr

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('new_password')
        p2 = cleaned_data.get('confirm_new_password')
        if p1 and p2 and p1 != p2:
            self.add_error('confirm_new_password', 'নতুন পাসওয়ার্ড দুটি মিলছে না।')
        if len(p1 or '') < 4:
            self.add_error('new_password', 'পাসওয়ার্ড কমপক্ষে ৪ অক্ষরের হতে হবে।')
        return cleaned_data


class AdminRegistrationForm(forms.ModelForm):
    first_name = forms.CharField(
        label="প্রথম নাম",
        required=True,
        widget=forms.TextInput(attrs={'class': 'w-full px-4 py-2.5 border border-gray-300 rounded-xl focus:ring-2 focus:ring-red-500 text-sm', 'placeholder': 'উদা: মোঃ শওন'})
    )
    last_name = forms.CharField(
        label="শেষ নাম",
        required=True,
        widget=forms.TextInput(attrs={'class': 'w-full px-4 py-2.5 border border-gray-300 rounded-xl focus:ring-2 focus:ring-red-500 text-sm', 'placeholder': 'উদা: রহমান'})
    )
    email = forms.EmailField(
        label="অ্যাডমিন ইমেইল *",
        required=True,
        widget=forms.EmailInput(attrs={'class': 'w-full px-4 py-2.5 border border-gray-300 rounded-xl focus:ring-2 focus:ring-red-500 text-sm', 'placeholder': 'admin@aponjon.org'})
    )
    phone = forms.CharField(
        label="মোবাইল নম্বর *",
        required=True,
        widget=forms.TextInput(attrs={'class': 'w-full px-4 py-2.5 border border-gray-300 rounded-xl focus:ring-2 focus:ring-red-500 text-sm', 'placeholder': '০১৭১১-XXXXXX'})
    )
    admin_secret = forms.CharField(
        label="অ্যাডমিন পিন / সিক্রেট কি (ঐচ্ছিক)",
        required=False,
        widget=forms.PasswordInput(attrs={'class': 'w-full px-4 py-2.5 border border-gray-300 rounded-xl focus:ring-2 focus:ring-red-500 text-sm', 'placeholder': 'ডিফল্ট: aponjon2026'})
    )
    password = forms.CharField(
        label="পাসওয়ার্ড *",
        widget=forms.PasswordInput(attrs={'class': 'w-full px-4 py-2.5 border border-gray-300 rounded-xl focus:ring-2 focus:ring-red-500 text-sm', 'placeholder': 'কমপক্ষে ৪ অক্ষরের পাসওয়ার্ড'})
    )
    confirm_password = forms.CharField(
        label="পাসওয়ার্ড নিশ্চিত করুন *",
        widget=forms.PasswordInput(attrs={'class': 'w-full px-4 py-2.5 border border-gray-300 rounded-xl focus:ring-2 focus:ring-red-500 text-sm', 'placeholder': 'একই পাসওয়ার্ড পুনরায় লিখুন'})
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'phone']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'w-full px-4 py-2.5 border border-gray-300 rounded-xl focus:ring-2 focus:ring-red-500 text-sm', 'placeholder': 'অ্যাডমিন ইউজারনেম'}),
        }

    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name', '').strip()
        if not first_name:
            raise forms.ValidationError("অ্যাডমিনের নাম প্রদান করা বাধ্যতামূলক।")
        return first_name

    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '').strip()
        digits = ''.join(filter(str.isdigit, phone))
        if not phone or len(digits) < 11:
            raise forms.ValidationError("একটি সঠিক ১১ ডিজিটের মোবাইল নম্বর প্রদান করা বাধ্যতামূলক।")
        return phone

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("এই ইমেইল দিয়ে ইতিমধ্যে একটি অ্যাকাউন্ট নিবন্ধিত আছে।")
        return email

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('password')
        p2 = cleaned_data.get('confirm_password')
        if p1 and p2 and p1 != p2:
            self.add_error('confirm_password', 'উভয় পাসওয়ার্ড হুবহু মিলছে না।')
        return cleaned_data


class PasswordResetEmailRequestForm(forms.Form):
    """Step 1: Enter email, phone number, or username to receive/view 6-digit verification code"""
    email = forms.CharField(
        label="নিবন্ধিত ইমেইল, মোবাইল নম্বর বা ইউজারনেম *",
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-red-500 text-sm',
            'placeholder': 'ইমেইল, মোবাইল (যেমন: ০১৭১১...) অথবা ইউজারনেম'
        })
    )

    def clean_email(self):
        val = self.cleaned_data.get('email', '').strip()
        if not val:
            raise forms.ValidationError("অনুগ্রহ করে আপনার ইমেইল, মোবাইল নম্বর বা ইউজারনেম লিখুন।")

        user = User.objects.filter(email__iexact=val).first()
        if not user:
            user = User.objects.filter(username__iexact=val).first()
        if not user:
            clean_digits = ''.join(filter(str.isdigit, val))
            if clean_digits and len(clean_digits) >= 6:
                user = User.objects.filter(phone__icontains=clean_digits).first()

        if not user:
            raise forms.ValidationError("প্রদত্ত তথ্য দিয়ে কোনো নিবন্ধিত অ্যাকাউন্ট পাওয়া যায়নি।")
        self.matched_user = user
        return val


class PasswordResetVerifyCodeForm(forms.Form):
    """Step 2: Enter 6-digit code received via email and set new password"""
    code = forms.CharField(
        label="৬-ডিজিটের ভেরিফিকেশন কোড *",
        max_length=6,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-red-500 text-center font-mono text-xl tracking-widest',
            'placeholder': '123456',
            'autocomplete': 'off'
        })
    )
    new_password = forms.CharField(
        label="নতুন পাসওয়ার্ড *",
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-2.5 border border-gray-300 rounded-xl focus:ring-2 focus:ring-red-500 text-sm',
            'placeholder': 'নতুন পাসওয়ার্ড লিখুন (কমপক্ষে ৪ অক্ষর)'
        })
    )
    confirm_new_password = forms.CharField(
        label="নতুন পাসওয়ার্ড নিশ্চিত করুন *",
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-2.5 border border-gray-300 rounded-xl focus:ring-2 focus:ring-red-500 text-sm',
            'placeholder': 'একই পাসওয়ার্ড পুনরায় লিখুন'
        })
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_code(self):
        code_input = self.cleaned_data.get('code', '').strip()
        from .models import PasswordResetCode
        reset_code = PasswordResetCode.objects.filter(user=self.user, code=code_input).first()
        if not reset_code or not reset_code.is_valid():
            raise forms.ValidationError("ভেরিফিকেশন কোডটি সঠিক নয় অথবা মেয়াদোত্তীর্ণ হয়ে গেছে (মেয়াদ ১৫ মিনিট)।")
        self.valid_code_obj = reset_code
        return code_input

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('new_password')
        p2 = cleaned_data.get('confirm_new_password')
        if p1 and p2 and p1 != p2:
            self.add_error('confirm_new_password', 'নতুন পাসওয়ার্ড দুটি মিলছে না।')
        if len(p1 or '') < 4:
            self.add_error('new_password', 'পাসওয়ার্ড কমপক্ষে ৪ অক্ষরের হতে হবে।')
        return cleaned_data
