from django import forms
from django.core import validators
from django.forms import DateInput
from jalali_date.fields import JalaliDateField
from jalali_date.widgets import AdminJalaliDateWidget

from account_module.models import Leave, Employee


class RegisterForm(forms.Form):
    username = forms.CharField(
        label='نام کاربری',
        widget=forms.TextInput(),
        validators=[
            validators.MaxLengthValidator(100)
        ]
    )
    email = forms.EmailField(
        label='ایمیل',
        widget=forms.EmailInput(),
        validators=[
            validators.MaxLengthValidator(100),
            validators.EmailValidator()
        ]
    )
    password = forms.CharField(
        label='کلمه عبور',
        widget=forms.PasswordInput(),
        validators=[
            validators.MaxLengthValidator(100)
        ]
    )
    confirm_password = forms.CharField(
        label='تکرار کلمه عبور',
        widget=forms.PasswordInput(),
        validators=[
            validators.MaxLengthValidator(100)
        ]
    )

    def clean_confirm_password(self):
        password = self.cleaned_data.get('password')
        confirm_password = self.cleaned_data.get('confirm_password')
        if password == confirm_password:
            return confirm_password
        raise forms.ValidationError('کلمه عبور و تکرار کلمه عبور یکسان نیستند')


class LoginForm(forms.Form):
    username = forms.CharField(
        label='نام کاربری',
        widget=forms.TextInput(),
        validators=[
            validators.MaxLengthValidator(100)
        ]
    )
    password = forms.CharField(
        label='کلمه عبور',
        widget=forms.PasswordInput(),
        validators=[
            validators.MaxLengthValidator(100)
        ]
    )


class ForgotPasswordForm(forms.Form):
    email = forms.EmailField(
        label='ایمیل',
        widget=forms.EmailInput(),
        validators=[
            validators.MaxLengthValidator(100),
            validators.EmailValidator()
        ]
    )


class ResetPasswordForm(forms.Form):
    password = forms.CharField(
        label='کلمه عبور',
        widget=forms.PasswordInput(),
        validators=[
            validators.MaxLengthValidator(100)
        ]
    )
    confirm_password = forms.CharField(
        label='تکرار کلمه عبور',
        widget=forms.PasswordInput(),
        validators=[
            validators.MaxLengthValidator(100)
        ]
    )


class LeaveForm(forms.ModelForm):
    employee = forms.ModelChoiceField(queryset=None, label="کارمند", widget=forms.Select(attrs={'class': 'text-center form-control'}))
    start_date = JalaliDateField(widget=AdminJalaliDateWidget(attrs={'class': 'text-center form-control jalali_date-date'}))
    end_date = JalaliDateField(widget=AdminJalaliDateWidget(attrs={'class': 'text-center form-control jalali_date-date'}))
    leave_type = forms.ChoiceField(choices=(('استحقاقی', 'استحقاقی'), ('استعلاجی', 'استعلاجی')), label='نوع مرخصی', widget=forms.Select(attrs={'class': 'text-center form-control'}))
    description = forms.CharField(label="توضیحات", required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 15}), max_length=100)
    def __init__(self, *args, user_workplace_code=None, **kwargs):
        super(LeaveForm, self).__init__(*args, **kwargs)
        # self.fields['start_date'] = JalaliDateField(
        #                                       widget=AdminJalaliDateWidget  # optional, to use default datepicker
        #                                       )
        # you can added a "class" to this field for use your datepicker!
        # self.fields['start_date'].widget.attrs.update({'class': 'jalali_date-date'})
        if user_workplace_code:
            self.fields['employee'].queryset = Employee.objects.filter(workplace_code=user_workplace_code)

    class Meta:
        model = Leave
        fields = ['employee', 'leave_type', 'leave_days', 'start_date', 'end_date', 'attachment', 'description']
        widgets = {
            'leave_days': forms.NumberInput(attrs={'class': 'text-center form-control'}),
            'attachment': forms.FileInput(attrs={'class': 'text-center form-control'}),
            # 'description': forms.Textarea(attrs={'class': 'form-control', 'rows':6}),
            # Consistent widget and styling
        }
        labels = {
            'employee': 'کارمند',
            'leave_days': 'تعداد روزهای مرخصی',
            'start_date': 'تاریخ شروع',
            'end_date': 'تاریخ پایان',
            'attachment': 'پیوست',
            'description': 'توضیحات',
        }
