from django.contrib import admin
from . import models


# Register your models here.
@admin.register(models.RainGauge)
class RainGaugeAdmin(admin.ModelAdmin):
    list_display = ['title', 'code', 'city', 'recent_rainfall']
    list_editable = ['code', 'city', 'recent_rainfall']


@admin.register(models.Station)
class StationAdmin(admin.ModelAdmin):
    list_filter = ['category', 'is_active']
    list_display = ['title', 'code', 'is_active', 'is_delete']
    list_editable = ['code', 'is_active']


# admin.site.register(models.Station, StationAdmin)
admin.site.register(models.StationCategory)
admin.site.register(models.StationTag)
admin.site.register(models.StationType)
admin.site.register(models.StationVisit)
admin.site.register(models.StationGallery)
# admin.site.register(models.RainGauge, RainGaugeAdmin)

