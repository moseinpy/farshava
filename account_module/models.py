from django.contrib.auth.models import AbstractUser
from django.db import models
from jalali_date import date2jalali


class User(AbstractUser):
    avatar = models.ImageField(upload_to='images/profile', verbose_name="تصویر آواتار", null=True, blank=True)
    email_active_user = models.CharField(max_length=100, verbose_name="کد فعال سازی ایمیل")
    about_user = models.TextField(default=False, blank=True, verbose_name="درباره شخص")
    address = models.TextField(null=True, blank=True, verbose_name="آدرس")

    class meta:
        verbose_name = "کاربر"
        verbose_name_plural = "کاربران"

    def __str__(self):
        if self.first_name is not '' and self.last_name is not '':
            return self.get_full_name()
        else:
            return self.email


class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="کاربر", null=True, blank=True)
    code_melli = models.CharField(max_length=10, verbose_name="کد ملی", null=True, blank=True)
    workplace_code = models.CharField(max_length=30, verbose_name="کدایستگاه")
    position = models.CharField(max_length=200, verbose_name="سمت")

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
