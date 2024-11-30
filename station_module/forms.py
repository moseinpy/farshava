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



class TableUpdate24hRainfallForm(forms.ModelForm):
    class Meta:
        model = Station
        fields = ['title', 'rainfall_24h', 'recent_rainfall', 'year_rainfall']

    # تنظیم فیلدهای بارشی به صورت اختیاری
    rainfall_24h = forms.FloatField(
        required=False,
        widget=forms.NumberInput(attrs={'min': 0, 'step': 0.1}),
        help_text='بارش 24 ساعت اخیر'
    )
    recent_rainfall = forms.FloatField(
        required=False,
        widget=forms.NumberInput(attrs={'min': 0, 'step': 0.1}),
        help_text='بارش اخیر'
    )
    year_rainfall = forms.FloatField(
        required=False,
        widget=forms.NumberInput(attrs={'min': 0, 'step': 0.1}),
        help_text='بارش سال زراعی'
    )

    def clean_rainfall_24h(self):
        rainfall = self.cleaned_data.get('rainfall_24h')
        if rainfall is not None and rainfall < 0:
            raise forms.ValidationError("مقدار بارش نمی‌تواند منفی باشد")
        return rainfall

    def clean_recent_rainfall(self):
        rainfall = self.cleaned_data.get('recent_rainfall')
        if rainfall is not None and rainfall < 0:
            raise forms.ValidationError("مقدار بارش نمی‌تواند منفی باشد")
        return rainfall

    def clean_year_rainfall(self):
        rainfall = self.cleaned_data.get('year_rainfall')
        if rainfall is not None and rainfall < 0:
            raise forms.ValidationError("مقدار بارش نمی‌تواند منفی باشد")
        return rainfall
from django.forms import modelformset_factory

TableUpdate24hRainfallFormSet = modelformset_factory(
    Station,
    form=TableUpdate24hRainfallForm,
    extra=0,
    can_delete=False
)
