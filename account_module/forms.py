from django import forms
from django.core import validators
from django.forms import DateInput
from jalali_date.fields import JalaliDateField
from jalali_date.widgets import AdminJalaliDateWidget

from account_module.models import Leave, Employee, WorkLog


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
    leave_type = forms.ChoiceField(choices=(('استحقاقی', 'استحقاقی'), ('استعلاجی', 'استعلاجی'), ('ساعتی', 'ساعتی')), label='نوع مرخصی', widget=forms.Select(attrs={'class': 'text-center form-control'}))
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




class WorkLogForm(forms.ModelForm):
    employee = forms.ModelChoiceField(queryset=Employee.objects.none(), label='کارمند')
    year = forms.ChoiceField(label='سال')
    month = forms.ChoiceField(label='ماه')

    class Meta:
        model = WorkLog
        fields = ['employee', 'year', 'month', 'day_shifts', 'night_shifts', 'leaves', 'nill_reports', 'late_early_reports', 'incorrect_reports', 'station_collaboration']

        def clean_day_shifts(self):
            day_shifts = self.cleaned_data.get('day_shifts')
            if day_shifts < 0 or day_shifts > 31:
                raise forms.ValidationError('تعداد شیفت روز باید بین 0 تا 31 باشد.')
            return day_shifts

        def clean_night_shifts(self):
            night_shifts = self.cleaned_data.get('night_shifts')
            if night_shifts < 0 or night_shifts > 31:
                raise forms.ValidationError('تعداد شیفت شب باید بین 0 تا 31 باشد.')
            return night_shifts

        def clean_leaves(self):
            leaves = self.cleaned_data.get('leaves')
            if leaves < 0 or leaves > 31:
                raise forms.ValidationError('تعداد مرخصی باید بین 0 تا 31 باشد.')
            return leaves

        def clean_nill_reports(self):
            nill_reports = self.cleaned_data.get('nill_reports')
            if nill_reports < 0 or nill_reports > 300:
                raise forms.ValidationError('تعداد عدم مخابره گزارش باید بین 0 تا 300 باشد.')
            return nill_reports

        def clean_late_early_reports(self):
            late_early_reports = self.cleaned_data.get('late_early_reports')
            if late_early_reports < 0 or late_early_reports > 300:
                raise forms.ValidationError('تعداد تاخیر و تعجیل در گزارش باید بین 0 تا 300 باشد.')
            return late_early_reports

        def clean_incorrect_reports(self):
            incorrect_reports = self.cleaned_data.get('incorrect_reports')
            if incorrect_reports < 0 or incorrect_reports > 300:
                raise forms.ValidationError('تعداد اشتباه در گزارش باید بین 0 تا 300 باشد.')
            return incorrect_reports

        def clean_station_collaboration(self):
            station_collaboration = self.cleaned_data.get('station_collaboration')
            if station_collaboration < -5 or station_collaboration > 5:
                raise forms.ValidationError('همکاری در امور ایستگاه باید بین -5 تا 5 باشد.')
            return station_collaboration

        def clean_employee(self):
            employee = self.cleaned_data.get('employee')
            if not employee:
                raise forms.ValidationError('لطفا نام کارمند را انتخاب کنید.')
            return employee


        widgets = {
            'day_shifts': forms.NumberInput(attrs={'min': 0, 'max': 31}),
            'night_shifts': forms.NumberInput(attrs={'min': 0, 'max': 31}),
            'leaves': forms.NumberInput(attrs={'min': 0, 'max': 31}),
            'nill_reports': forms.NumberInput(attrs={'min': 0, 'max': 300}),
            'late_early_reports': forms.NumberInput(attrs={'min': 0, 'max': 300}),
            'incorrect_reports': forms.NumberInput(attrs={'min': 0, 'max': 300}),
            'station_collaboration': forms.NumberInput(attrs={'min': -5, 'max': 5}),
        }
        error_messages = {
            'day_shifts': {
                'max_value': 'مطمئن شوید تعداد شیفت روز  کوچکتر یا مساوی 31 است.',
                'min_value': 'مطمئن شوید تعداد شیفت روز بزرگتر یا مساوی 0 است.'
            },
            'night_shifts': {
                'max_value': 'مطمئن شوید تعداد شیفت شب کوچکتر یا مساوی 31 است.',
                'min_value': 'مطمئن شوید تعداد شیفت شب بزرگتر یا مساوی 0 است.'
            },
            'leaves': {
                'max_value': 'مطمئن شوید تعداد روز مرخصی کوچکتر یا مساوی 31 است.',
                'min_value': 'مطمئن شوید تعداد روز مرخصی بزرگتر یا مساوی 0 است.'
            },
            'nill_reports': {
                'max_value': 'مطمئن شوید تعداد عدم مخابره در گزارش کوچکتر یا مساوی 300 است.',
                'min_value': 'مطمئن شوید تعداد عدم مخابره در گزارش بزرگتر یا مساوی 0 است.'
            },
            'late_early_reports': {
                'max_value': 'مطمئن شوید تعداد تاخیر و تعجیل در گزارش کوچکتر یا مساوی 300 است.',
                'min_value': 'مطمئن شوید تعداد تاخیر و تعجیل در گزارش بزرگتر یا مساوی 0 است.'
        },
            'incorrect_reports': {
                'max_value': 'مطمئن شوید تعداد اشتباه در گزارش کوچکتر یا مساوی 300 است.',
                'min_value': 'مطمئن شوید تعداد اشتباه در گزارش بزرگتر یا مساوی 0 است.'
            },
            'station_collaboration': {
                'max_value': 'مطمئن شوید تعداد ساعت همکاری در امور ایستگاه کوچکتر یا مساوی 5 است.',
                'min_value': 'مطمئن شوید تعداد ساعت همکاری در امور ایستگاه بزرگتر یا مساوی -5 است.'
            },
             'employee': {
            'required': 'نام کارمند باید انتخاب گردد.'
            }
        }

    def __init__(self, *args, **kwargs):
        workplace_code = kwargs.pop('workplace_code', None)
        years = kwargs.pop('years', [])
        months = kwargs.pop('months', [])
        super().__init__(*args, **kwargs)
        if workplace_code:
            self.fields['employee'].queryset = Employee.objects.filter(workplace_code=workplace_code)
        self.fields['year'].choices = [(year, year) for year in years]
        self.fields['month'].choices = [(month[0], month[1]) for month in months]
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'



# class YearMonthForm(forms.Form):
#     year = forms.ChoiceField(label='سال', required=False)
#     month = forms.ChoiceField(label='ماه', required=False)
#
#     def __init__(self, *args, **kwargs):
#         super(YearMonthForm, self).__init__(*args, **kwargs)
#         years = WorkLog.objects.values_list('year', flat=True).distinct().order_by('-year')
#         months = WorkLog.objects.values_list('month', flat=True).distinct().order_by('month')
#         self.fields['year'].choices = [(year, year) for year in years]
#         self.fields['month'].choices = [(month, month) for month in months]


class YearMonthForm(forms.Form):
    year = forms.ChoiceField(label='سال', required=False)
    month = forms.ChoiceField(label='ماه', required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # سال‌ها را به ترتیب نزولی می‌آوریم
        years = WorkLog.objects.values_list('year', flat=True).distinct().order_by('-year')
        self.fields['year'].choices = [(year, year) for year in years]

        # ترتیب صحیح ماه‌های شمسی
        month_order = [
            'فروردین', 'اردیبهشت', 'خرداد', 'تیر', 'مرداد', 'شهریور',
            'مهر', 'آبان', 'آذر', 'دی', 'بهمن', 'اسفند'
        ]

        # ماه‌هایی که در دیتابیس وجود دارند
        db_months = list(WorkLog.objects.values_list('month', flat=True).distinct())

        # مرتب‌سازی ماه‌ها بر اساس ترتیب تقویمی
        sorted_months = [m for m in month_order if m in db_months]

        # تنظیم گزینه‌ها در فیلد ماه
        self.fields['month'].choices = [(m, m) for m in sorted_months]
