from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.urls import reverse
from account_module.models import User
from django.utils import timezone


# Create your models here.

class StationCategory(models.Model):
    title = models.CharField(max_length=300, db_index=True, verbose_name='عنوان')
    url_title = models.CharField(max_length=300, db_index=True, verbose_name='عنوان در url')
    is_active = models.BooleanField(verbose_name='فعال / غیرفعال')
    is_delete = models.BooleanField(verbose_name='حذف شده / نشده')

    def __str__(self):
        return f'( {self.title} - {self.url_title} )'

    class Meta:
        verbose_name = 'دسته بندی'
        verbose_name_plural = 'دسته بندی ها'


class StationType(models.Model):
    title = models.CharField(max_length=300, verbose_name='نوع', db_index=True)
    url_title = models.CharField(max_length=300, verbose_name='عنوان در url', db_index=True)
    is_active = models.BooleanField(verbose_name='فعال / غیرفعال')

    class Meta:
        verbose_name = 'نوع'
        verbose_name_plural = 'انواع'

    def __str__(self):
        return self.title


class Station(models.Model):
    title = models.CharField(max_length=300, verbose_name='نام')
    city = models.CharField(max_length=300, verbose_name='شهرستان', null=True, blank=True)
    code = models.CharField(max_length=6, unique=True, blank=False, verbose_name='کد')
    longitude = models.DecimalField(max_digits=9, decimal_places=6, verbose_name='طول جغرافیایی', null=True, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, verbose_name='عرض جغرافیایی', null=True, blank=True)
    elevation = models.IntegerField(validators=[MaxValueValidator(3000)], verbose_name='ارتفاع', null=True, blank=True)
    category = models.ManyToManyField(
        StationCategory,
        related_name='station_categories',
        verbose_name='دسته بندی ها')
    type = models.ForeignKey(StationType, on_delete=models.CASCADE, verbose_name='نوع', null=True, blank=True)
    parent_station = models.ForeignKey('Station', on_delete=models.SET_NULL, verbose_name='ایستگاه والد', null=True, blank=True)
    image = models.ImageField(upload_to="images/stations", null=True, blank=True, verbose_name='تصویر ایستگاه')
    rainfall_3h = models.FloatField(validators=[MinValueValidator(0)], verbose_name='بارندگی 3 ساعت اخیر', null=True, blank=True)
    rainfall_24h = models.FloatField(validators=[MinValueValidator(0)], verbose_name='بارندگی 24 ساعت اخیر', null=True, blank=True)
    recent_rainfall = models.FloatField(validators=[MinValueValidator(0)] ,verbose_name='بارندگی اخیر', null=True, blank=True)
    last_rainfall_date_time = models.DateTimeField(verbose_name='تاریخ ثبت بارندگی اخیر', null=True, blank=True)
    year_rainfall = models.FloatField(validators=[MinValueValidator(0)] ,verbose_name='بارندگی سال', null=True, blank=True)
    max_temperature = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name="دمای بیشینه")
    min_temperature = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name="دمای کمینه")
    soil_min_temperature = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name="دمای کمینه خاک")
    time_update_temp = models.DateTimeField(verbose_name='تاریخ بروزرسانی دما', null=True, blank=True, default=None)
    short_description = models.CharField(max_length=360, db_index=True, null=True, blank=True, verbose_name='توضیحات کوتاه')
    description = models.TextField(verbose_name='توضیحات اصلی', db_index=True, null=True, blank=True)
    slug = models.SlugField(default="", null=True, db_index=True, blank=True, max_length=200, unique=True,verbose_name='عنوان در url')
    is_active = models.BooleanField(default=False, verbose_name='فعال / غیرفعال')
    is_delete = models.BooleanField(verbose_name='حذف شده / نشده')



    def get_location(self):
        if self.longitude and self.latitude:
            return Point(self.longitude, self.latitude)
        else:
            return None

    def get_elevation_label(self):
        if self.elevation:
            return f"{self.elevation} متر "
        else:
            return "ارتفاع نامشخص"

    def save(self, *args, **kwargs):
        # بررسی اینکه آیا آبجکت قبلاً در پایگاه داده وجود دارد
        try:
            original = Station.objects.get(pk=self.pk)

            # بررسی تغییرات در مقادیر دما
            is_temperature_changed = (
                (original.min_temperature != self.min_temperature) or
                (original.max_temperature != self.max_temperature) or
                (original.soil_min_temperature != self.soil_min_temperature)
            )

            if is_temperature_changed:
                self.time_update_temp = timezone.now()

            # بررسی تغییرات در مقدار بارش اخیر
            is_rainfall_changed = (original.recent_rainfall != self.recent_rainfall)

            if is_rainfall_changed:
                self.last_rainfall_date_time = timezone.now()

        except Station.DoesNotExist:
            # برای آبجکت‌های جدید، اگر مقدار دما یا بارش تغییر کرده باشد، زمان را تنظیم می‌کنیم
            if self.min_temperature or self.max_temperature or self.soil_min_temperature:
                self.time_update_temp = timezone.now()

            if self.recent_rainfall is not None:
                self.last_rainfall_date_time = timezone.now()

        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('station-detail', args=[self.slug])

    def __str__(self):
        return f"{self.title} ({self.code})"

    class Meta:
        verbose_name = 'ایستگاه'
        verbose_name_plural = 'ایستگاه ها'

    def formatted_max_temperature(self):
        if self.max_temperature is not None:
            return f"{self.max_temperature:,.2f}"
        return '-'

    def formatted_min_temperature(self):
        if self.min_temperature is not None:
            return f"{self.min_temperature:,.2f}"
        return '-'

    def formatted_soil_min_temperature(self):
        if self.soil_min_temperature is not None:
            return f"{self.soil_min_temperature:,.2f}"
        return '-'



# class Station(models.Model):
#     title = models.CharField(max_length=300, verbose_name='نام')
#     city = models.CharField(max_length=300, verbose_name='شهرستان', null=True, blank=True)
#     code = models.CharField(max_length=6, unique=True, blank=False, verbose_name='کد')
#     longitude = models.DecimalField(max_digits=9, decimal_places=6, verbose_name='طول جغرافیایی', null=True, blank=True)
#     latitude = models.DecimalField(max_digits=9, decimal_places=6, verbose_name='عرض جغرافیایی', null=True, blank=True)
#     elevation = models.IntegerField(validators=[MaxValueValidator(3000)], verbose_name='ارتفاع', null=True, blank=True)
#     category = models.ManyToManyField(
#         StationCategory,
#         related_name='station_categories',
#         verbose_name='دسته بندی ها')
#     type = models.ForeignKey(StationType, on_delete=models.CASCADE, verbose_name='نوع', null=True, blank=True)
#     parent_station = models.ForeignKey('Station', on_delete=models.SET_NULL, verbose_name='ایستگاه والد', null=True, blank=True)
#     image = models.ImageField(upload_to="images/stations", null=True, blank=True, verbose_name='تصویر ایستگاه')
#     rainfall_3h = models.FloatField(validators=[MinValueValidator(0)], verbose_name='بارندگی 3 ساعت اخیر', null=True, blank=True)
#     rainfall_24h = models.FloatField(validators=[MinValueValidator(0)], verbose_name='بارندگی 24 ساعت اخیر', null=True, blank=True)
#     recent_rainfall = models.FloatField(validators=[MinValueValidator(0)] ,verbose_name='بارندگی اخیر', null=True, blank=True)
#     last_rainfall_date_time = models.DateTimeField(verbose_name='تاریخ ثبت بارندگی اخیر', null=True, blank=True)
#     year_rainfall = models.FloatField(validators=[MinValueValidator(0)] ,verbose_name='بارندگی سال', null=True, blank=True)
#     max_temperature = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name="دمای بیشینه")
#     min_temperature = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name="دمای کمینه")
#     soil_min_temperature = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name="دمای کمینه خاک")
#     time_update_temp = models.DateTimeField(verbose_name='تاریخ بروزرسانی دما', null=True, blank=True, default=None)
#     short_description = models.CharField(max_length=360, db_index=True, null=True, blank=True, verbose_name='توضیحات کوتاه')
#     description = models.TextField(verbose_name='توضیحات اصلی', db_index=True, null=True, blank=True)
#     slug = models.SlugField(default="", null=True, db_index=True, blank=True, max_length=200, unique=True,verbose_name='عنوان در url')
#     is_active = models.BooleanField(default=False, verbose_name='فعال / غیرفعال')
#     is_delete = models.BooleanField(verbose_name='حذف شده / نشده')
#
#     def get_location(self):
#         if self.longitude and self.latitude:
#             return Point(self.longitude, self.latitude)
#         else:
#             return None
#
#     def get_elevation_label(self):
#         if self.elevation:
#             return f"{self.elevation} متر "
#         else:
#             return "ارتفاع نامشخص"
#
#     def save(self, *args, **kwargs):
#         # مقداردهی خودکار time_update_temp هنگام تغییر دما
#         if self.max_temperature or self.min_temperature or self.soil_min_temperature:
#             self.time_update_temp = timezone.now()
#         super().save(*args, **kwargs)
#
#     def save(self, *args, **kwargs):
#         # بررسی اینکه آیا آبجکت قبلاً در پایگاه داده وجود دارد
#         try:
#             original = Station.objects.get(pk=self.pk)
#
#             # مقایسه دقیق مقادیر بارندگی اخیر
#             # استفاده از None-safe comparison
#             is_temperature_changed = (
#                     (original.min_temperature is None and self.min_temperature is not None) or
#                     (original.min_temperature is not None and self.min_temperature is None) or
#                     (original.min_temperature != self.min_temperature)
#             )
#
#             # اگر مقدار بارش اخیر تغییر کرده، زمان را به‌روز کن
#             if is_temperature_changed:
#                 self.time_update_temp = timezone.now()
#
#         except Station.DoesNotExist:
#             # برای آبجکت‌های جدید، اگر مقدار بارش اخیر وجود دارد، زمان را تنظیم کن
#             if self.min_temperature is not None:
#                 self.min_temperature = timezone.now()
#
#         super().save(*args, **kwargs)
#
#
#     def get_absolute_url(self):
#         return reverse('station-detail', args=[self.slug])
#
#     def save(self, *args, **kwargs):
#         # بررسی اینکه آیا آبجکت قبلاً در پایگاه داده وجود دارد
#         try:
#             original = Station.objects.get(pk=self.pk)
#
#             # مقایسه دقیق مقادیر بارندگی اخیر
#             # استفاده از None-safe comparison
#             is_rainfall_changed = (
#                     (original.recent_rainfall is None and self.recent_rainfall is not None) or
#                     (original.recent_rainfall is not None and self.recent_rainfall is None) or
#                     (original.recent_rainfall != self.recent_rainfall)
#             )
#
#             # اگر مقدار بارش اخیر تغییر کرده، زمان را به‌روز کن
#             if is_rainfall_changed:
#                 self.last_rainfall_date_time = timezone.now()
#
#         except Station.DoesNotExist:
#             # برای آبجکت‌های جدید، اگر مقدار بارش اخیر وجود دارد، زمان را تنظیم کن
#             if self.recent_rainfall is not None:
#                 self.last_rainfall_date_time = timezone.now()
#
#         super().save(*args, **kwargs)
#     def __str__(self):
#         return f"{self.title} ({self.code})"
#
#     class Meta:
#         verbose_name = 'ایستگاه'
#         verbose_name_plural = 'ایستگاه ها'

class StationTag(models.Model):
    caption = models.CharField(max_length=300, db_index=True, verbose_name='عنوان')
    station = models.ForeignKey(Station, on_delete=models.CASCADE, related_name='station_tags')

    class Meta:
        verbose_name = 'تگ ایستگاه'
        verbose_name_plural = 'تگ های ایستگاه'

    def __str__(self):
        return self.caption


class StationVisit(models.Model):
    station = models.ForeignKey(Station, on_delete=models.CASCADE, verbose_name='ایستگاه')
    ip = models.CharField(max_length=30, verbose_name='آی پی کاربر')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='کاربر', null=True, blank=True)

    def __str__(self):
        return f'{self.station} / {self.ip}'

    class Meta:
        verbose_name = 'بازدید ایستگاه'
        verbose_name_plural = 'بازدید های ایستگاه'


class StationGallery(models.Model):
    station = models.ForeignKey('Station', on_delete=models.CASCADE, verbose_name='ایستگاه')
    image = models.ImageField(upload_to="images/station-gallery", verbose_name='تصویر')

    def __str__(self):
        return self.station.title

    class Meta:
        verbose_name = 'تصویر گالری'
        verbose_name_plural = 'گالری تصاویر'


