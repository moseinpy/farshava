from django.contrib.auth.models import AbstractUser
from django.db import models
from jalali_date import date2jalali
from django.utils import timezone
from django.core.validators import MaxValueValidator, MinValueValidator




class User(AbstractUser):
    avatar = models.ImageField(upload_to='images/profile', verbose_name="تصویر آواتار", null=True, blank=True)
    email_active_user = models.CharField(max_length=100, verbose_name="کد فعال سازی ایمیل")
    about_user = models.TextField(default=False, blank=True, verbose_name="درباره شخص")
    address = models.TextField(null=True, blank=True, verbose_name="آدرس")

    class Meta:
        verbose_name = "کاربر"
        verbose_name_plural = "کاربران"

    def __str__(self):
        if self.first_name is not '' and self.last_name is not '':
            return self.get_full_name()
        else:
            return self.email


class Employee(models.Model):
    ROLE_CHOICES = [
        ('responsible', 'مسئول'),
        ('non_responsible', 'غیر مسئول'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="کاربر", null=True, blank=True)
    code_melli = models.CharField(max_length=10, verbose_name="کد ملی", null=True, blank=True)
    workplace_code = models.CharField(max_length=30, verbose_name="کدایستگاه")
    position = models.CharField(max_length=200, verbose_name="سمت")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='non_responsible', verbose_name="نقش")


    # سایر فیلدهای مربوط به کارمند

    def __str__(self):
        return self.user.get_full_name()

    class Meta:
        verbose_name = "کارمند"
        verbose_name_plural = "کارمندان"


class Leave(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, verbose_name="کارمند")
    leave_type = models.CharField(max_length=100, verbose_name="نوع مرخصی")
    leave_days = models.IntegerField(verbose_name="تعداد روز مرخصی")
    start_date = models.DateField(verbose_name="تاریخ شروع مرخصی")
    end_date = models.DateField(verbose_name="تاریخ پایان مرخصی")
    attachment = models.FileField(upload_to='attachments/', verbose_name="آپلود فایل")
    description = models.TextField(verbose_name="توضیحات", blank=True)

    def get_jalali_start_date(self):
        return date2jalali(self.start_date)

    def get_jalali_end_date(self):
        return date2jalali(self.end_date)

    def __str__(self):
        return f"{self.employee.user.get_full_name()} - {self.leave_type}"

    class Meta:
        verbose_name = "مرخصی"
        verbose_name_plural = "مرخصی‌ها"

class WorkLog(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, verbose_name="کارمند")
    year = models.IntegerField(verbose_name="سال")
    month = models.CharField(max_length=20, verbose_name="ماه")
    day_shifts = models.IntegerField(
        verbose_name="تعداد شیفت روز",
        validators=[MinValueValidator(0), MaxValueValidator(31)],
        error_messages={
            'min_value': 'مطمئن شوید این مقدار بزرگتر یا مساوی 0 است.',
            'max_value': 'مطمئن شوید این مقدار کوچکتر یا مساوی 31 است.'
        }
    )
    night_shifts = models.IntegerField(
        verbose_name="تعداد شیفت شب",
        validators=[MinValueValidator(0), MaxValueValidator(31)],
        error_messages={
            'min_value': 'مطمئن شوید این مقدار بزرگتر یا مساوی 0 است.',
            'max_value': 'مطمئن شوید این مقدار کوچکتر یا مساوی 31 است.'
        }
    )
    leaves = models.IntegerField(
        verbose_name="تعداد مرخصی",
        validators=[MinValueValidator(0), MaxValueValidator(31)],
        error_messages={
            'min_value': 'مطمئن شوید این مقدار بزرگتر یا مساوی 0 است.',
            'max_value': 'مطمئن شوید این مقدار کوچکتر یا مساوی 31 است.'
        }
    )
    nill_reports = models.IntegerField(
        verbose_name="تعداد عدم مخابره در گزارش",
        validators=[MinValueValidator(0), MaxValueValidator(300)],
        error_messages={
            'min_value': 'مطمئن شوید این مقدار بزرگتر یا مساوی 0 است.',
            'max_value': 'مطمئن شوید این مقدار کوچکتر یا مساوی 300 است.'
        }
    )
    late_early_reports = models.IntegerField(
        verbose_name="تعداد تاخیر و تعجیل در گزارش",
        validators=[MinValueValidator(0), MaxValueValidator(300)],
        error_messages={
            'min_value': 'مطمئن شوید این مقدار بزرگتر یا مساوی 0 است.',
            'max_value': 'مطمئن شوید این مقدار کوچکتر یا مساوی 300 است.'
        }
    )
    incorrect_reports = models.IntegerField(
        verbose_name="تعداد اشتباه در گزارش",
        validators=[MinValueValidator(0), MaxValueValidator(300)],
        error_messages={
            'min_value': 'مطمئن شوید این مقدار بزرگتر یا مساوی 0 است.',
            'max_value': 'مطمئن شوید این مقدار کوچکتر یا مساوی 300 است.'
        }
    )
    station_collaboration = models.IntegerField(
        verbose_name="همکاری در امورات ایستگاه",
        validators=[MinValueValidator(-5), MaxValueValidator(5)],
        error_messages={
            'min_value': 'مطمئن شوید این مقدار بزرگتر یا مساوی -5 است.',
            'max_value': 'مطمئن شوید این مقدار کوچکتر یا مساوی 5 است.'
        }
    )
    created_at = models.DateTimeField(default=timezone.now, verbose_name="زمان ثبت", editable=False)


    def __str__(self):
        return f"{self.employee.user.get_full_name()} - {self.year} - {self.month}"

    class Meta:
        verbose_name = "کارکرد ماهانه"
        verbose_name_plural = "کارکردهای ماهانه"
        constraints = [
            models.UniqueConstraint(fields=['employee', 'year', 'month'], name='unique_worklog_per_month')
        ]