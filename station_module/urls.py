from django.urls import path
from . import views

urlpatterns = [
    path('', views.StationListView.as_view(), name='station-list'),
    path('cat/<cat>', views.StationListView.as_view(), name='station-categories-list'),
    path('type/<type>', views.StationListView.as_view(), name='station-list-by-types'),
    path('station-favorite', views.AddStationFavorite.as_view(), name='station-favorite'),
    path('<slug:slug>', views.StationDetailView.as_view(), name='station-detail'),
    path('rain-gauge-table/', views.RainGaugeTableView.as_view(), name='rain-gauge-table'),
    path('save-rain-gauge-value/', views.save_rain_gauge_value, name='save-rain-gauge-value'),
    path('recent-rain-gauge/', views.recent_rain_gauge, name='recent-rain-gauge'),
    path('rain-gauges-export-xls/', views.rain_gauges_export_xls, name='rain_gauges_export_xls'),
    path('rain-gauges-export-lat-long-xls/', views.rain_gauges_export_lat_long_xls, name='rain_gauges_export_lat_long_xls'),
    path('table-update-rainfall/', views.table_update_rainfall, name='table_update_rainfall'),
    path('stations-table-3h-recent-rainfall/', views.stations_table_3h_recent_rainfall, name='stations_table_3h_recent_rainfall'),
]
