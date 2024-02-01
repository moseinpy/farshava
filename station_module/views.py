import datetime

import openpyxl
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.http import HttpRequest
from django.http import HttpResponse
from django.shortcuts import redirect
from django.shortcuts import render
from django.utils import timezone
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, DetailView
from django_tables2 import RequestConfig
from openpyxl.styles import Font, Alignment

from site_module.models import SiteBanner
from utils.convertors import group_list
from utils.http_service import get_client_ip
from .models import Station
from .models import StationCategory, StationType, StationVisit, StationGallery
from .tables import RecentRainGaugeTable


class StationListView(ListView):
    template_name = 'station_module/station_list.html'
    model = Station
    context_object_name = 'stations'
    ordering = ['-code']
    paginate_by = 3

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(StationListView, self).get_context_data()
        context['banners'] = SiteBanner.objects.filter(is_active=True, position__iexact='station_list')
        return context

    def get_queryset(self):
        query = super(StationListView, self).get_queryset()
        query = query.exclude(category__url_title__iexact='rain-gauge')
        category_name = self.kwargs.get('cat')
        type_name = self.kwargs.get('type')

        if type_name is not None:
            query = query.filter(type__url_title__iexact=type_name)
            print(query.query)

        if category_name is not None:
            query = query.filter(category__url_title__iexact=category_name)
            print(query.query)
        return query


class StationDetailView(DetailView):
    template_name = 'station_module/station_detail.html'
    model = Station

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        loaded_station = self.object
        request = self.request
        favorite_station_id = request.session.get('station_favorites')
        context['is_favorite'] = favorite_station_id == str(loaded_station.id)
        context['banners'] = SiteBanner.objects.filter(is_active=True, position__iexact='station_detail')
        galleries = list(StationGallery.objects.filter(station_id=loaded_station.id).all())
        galleries.insert(0, loaded_station)
        context['station_galleries_group'] = group_list(galleries, 3)
        context['related_stations'] = group_list(
            list(Station.objects.filter(type_id=loaded_station.type_id).exclude(pk=loaded_station.id).all()[:12]), 3)
        user_ip = get_client_ip(self.request)
        user_id = None
        if self.request.user.is_authenticated:
            user_id = self.request.user.id

        has_been_visited = StationVisit.objects.filter(ip__iexact=user_ip, station_id=loaded_station.id).exists()
        if not has_been_visited:
            new_visit = StationVisit(station=loaded_station, ip=user_ip, user_id=user_id)
            new_visit.save()
        return context


class AddStationFavorite(View):
    def post(self, request):
        station_id = request.POST['station_id']
        station = Station.objects.get(pk=station_id)
        request.session['station_favorites'] = station_id
        return redirect(station.get_absolute_url())


def station_categories_component(request: HttpRequest):
    station_categories = StationCategory.objects.annotate(stations_count=Count('station_categories')).filter(
        is_active=True, is_delete=False)
    context = {
        'categories': station_categories
    }
    # station_categories = StationCategory.objects.filter(is_active=True, is_delete=False)
    # context = {
    #     'categories': station_categories
    # }
    return render(request, 'station_module/components/station_categories_component.html', context)


def station_types_component(request: HttpRequest):
    station_types = StationType.objects.annotate(stations_count=Count('station')).filter(is_active=True)
    context = {
        'types': station_types
    }
    return render(request, 'station_module/components/station_type_component.html', context)


class RainGaugeTableView(View):
    template_name = 'station_module/rain_gauge_table.html'

    def get(self, request, *args, **kwargs):
        current_user = request.user
        if hasattr(current_user, 'employee'):
            workplace_code = ''
            workplace_code = current_user.employee.workplace_code
            print(workplace_code)
        else:
            print('no employee')
        rain_gauges = Station.objects.filter(parent_station__code__exact=workplace_code).order_by('-recent_rainfall')
        return render(request, self.template_name, {'rain_gauges': rain_gauges})


@csrf_exempt
def save_rain_gauge_value(request):
    id = request.POST.get('id')
    value = request.POST.get('value')

    rain_gauge = Station.objects.get(pk=id)
    rain_gauge.recent_rainfall = float(value)
    rain_gauge.last_rainfall_date_time = timezone.now()
    rain_gauge.save()

    return HttpResponse('Data successfully saved.')


@login_required
def rain_gauges_export_xls(request):
    today = timezone.now()
    yesterday = today - datetime.timedelta(days=1)
    recent_rain = Station.objects.filter(last_rainfall_date_time__range=(yesterday, today)).order_by('-recent_rainfall')
    table = RecentRainGaugeTable(recent_rain)
    RequestConfig(request).configure(table)

    wb = openpyxl.Workbook()
    ws = wb.active

    # Set right-to-left direction
    ws.sheet_view.rightToLeft = True

    # Write table headers
    headers = ['ردیف', 'شهرستان', 'نام', 'مقدار بارندگی (میلیمتر)']
    header_font = Font(bold=True, size=12, color='000000')
    header_fill = Alignment(horizontal='center', vertical='center')
    for col_num, header in enumerate(headers, 1):
        ws.cell(row=1, column=col_num, value=header).font = header_font

    # Write table rows
    for row_num, row in enumerate(table.rows, 2):
        ws.cell(row=row_num, column=1, value=row_num - 1).alignment = header_fill  # Add row number value
        for col_num, cell in enumerate(row, 2):  # Start column index from 2
            excel_cell = ws.cell(row=row_num, column=col_num, value=str(cell))
            excel_cell.alignment = Alignment(horizontal='center', vertical='center')

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=بارندگی اخیر مورخه.xlsx'
    wb.save(response)

    return response


def recent_rain_gauge(request):
    today = timezone.now()
    yesterday = today - datetime.timedelta(days=1)
    recent_rain = Station.objects.filter(last_rainfall_date_time__range=(yesterday, today)).order_by('-recent_rainfall')
    table = RecentRainGaugeTable(recent_rain)
    RequestConfig(request).configure(table)

    return render(request, 'station_module/recent_rain_gauge.html', {'table': table})


