from django import forms
from django.forms import inlineformset_factory
from .models import RainGauge, Station

class RainGaugeForm(forms.ModelForm):
    class Meta:
        model = RainGauge
        fields = ['row','city', 'title', 'recent_rainfall']


RainGaugeFormSet = inlineformset_factory(Station, RainGauge, form=RainGaugeForm, extra=0)

