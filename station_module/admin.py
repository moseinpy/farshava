from django.contrib import admin
from . import models


@admin.register(models.Station)
class StationAdmin(admin.ModelAdmin):
    list_filter = ['category', 'is_active']
    list_display = ['title', 'code', 'latitude', 'longitude', 'elevation']
    list_editable = ['latitude', 'longitude', 'elevation']


# admin.site.register(models.Station, StationAdmin)
admin.site.register(models.StationCategory)
admin.site.register(models.StationTag)
admin.site.register(models.StationType)
admin.site.register(models.StationVisit)
admin.site.register(models.StationGallery)
