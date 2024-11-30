from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.urls import reverse
from account_module.models import User


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
#     recent_rainfall = models.FloatField(validators=[MinValueValidator(0)] ,verbose_name='بارندگی اخیر', null=True, blank=True)
#     last_rainfall_date_time = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ثبت بارندگی اخیر', null=True, blank=True)
#     year_rainfall = models.FloatField(verbose_name='بارندگی سال', null=True, blank=True)
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
#     def get_absolute_url(self):
#         return reverse('station-detail', args=[self.slug])
#
#     def save(self, *args, **kwargs):
#         # self.slug = slugify(self.code)
#         super().save(*args, **kwargs)
#
#     def __str__(self):
#         return f"{self.title} ({self.code})"
#
#     class Meta:
#         verbose_name = 'ایستگاه'
#         verbose_name_plural = 'ایستگاه ها'

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
    last_rainfall_date_time = models.DateTimeField(auto_now=True, verbose_name='تاریخ ثبت بارندگی اخیر', null=True, blank=True)
    year_rainfall = models.FloatField(validators=[MinValueValidator(0)] ,verbose_name='بارندگی سال', null=True, blank=True)
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

    def get_absolute_url(self):
        return reverse('station-detail', args=[self.slug])

    def save(self, *args, **kwargs):
        # self.slug = slugify(self.code)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} ({self.code})"

    class Meta:
        verbose_name = 'ایستگاه'
        verbose_name_plural = 'ایستگاه ها'

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


