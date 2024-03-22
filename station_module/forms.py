from django import forms
from .models import Station

class StationRainModelForm(forms.ModelForm):
    class Meta:
        model = Station
        fields = ["title", "city", "recent_rainfall"]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-control',
            }),
            'recent_rainfall': forms.NumberInput(attrs={
                'class': 'form-control',
            }),
        }


