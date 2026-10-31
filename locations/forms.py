from django import forms
from .models import Location

class LocationForm(forms.ModelForm):
    class Meta:
        model = Location
        fields = ['address', 'area', 'thana', 'city', 'postalCode', 'latitude', 'longitude']
        widgets = {
            'address': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-red-500', 'placeholder': 'e.g., Road 27, House 14'}),
            'area': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-red-500', 'placeholder': 'e.g., Dhanmondi 27'}),
            'thana': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-red-500', 'placeholder': 'e.g., Dhanmondi'}),
            'city': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-red-500', 'placeholder': 'e.g., Dhaka'}),
            'postalCode': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-red-500', 'placeholder': 'e.g., 1209'}),
            'latitude': forms.NumberInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-red-500', 'step': '0.0001', 'id': 'id_latitude'}),
            'longitude': forms.NumberInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-red-500', 'step': '0.0001', 'id': 'id_longitude'}),
        }
