import datetime
import json
import os
import folium
import openpyxl
from django.db.models import Q
from openpyxl.utils import get_column_letter
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.http import HttpRequest
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, DetailView
from openpyxl.styles import Font, Alignment, Border, PatternFill, Side
from site_module.models import SiteBanner
from utils.http_service import get_client_ip
from utils.convertors import group_list
from .models import StationCategory, StationType, StationVisit, StationGallery
from django.http import HttpResponse
from django.views import View
from django_tables2 import RequestConfig
from .tables import RecentRainGaugeTable, RecentRainGaugeLatLongTable
from django.shortcuts import render, redirect
from .models import Station




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
    recent_rain = Station.objects.filter(last_rainfall_date_time__date__gte=yesterday).order_by('-recent_rainfall')
    table = RecentRainGaugeTable(recent_rain)
    RequestConfig(request).configure(table)

    wb = openpyxl.Workbook()
    ws = wb.active

    # Set right-to-left direction
    ws.sheet_view.rightToLeft = True

    # Write table headers
    headers = ['ردیف', 'شهرستان', 'نام', 'مقدار بارندگی (میلیمتر)', 'زمان ثبت بارش']
    header_font = Font(bold=True, size=12, color='000000')
    header_fill = PatternFill(start_color='D3D3D3', end_color='D3D3D3', fill_type='solid')
    border = Border(left=Side(style='thin'), right=Side(style='thin'), top=Side(style='thin'),
                    bottom=Side(style='thin'))

    for col_num, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col_num, value=header)
        cell.font = header_font
        cell.alignment = Alignment(horizontal='center', vertical='center')
        cell.border = border

    # Write table rows
    row_color = 'FFFFFF'  # Start with a white color for the first row
    for row_num, row in enumerate(table.rows, 2):
        ws.cell(row=row_num, column=1, value=row_num - 1).alignment = Alignment(horizontal='center', vertical='center')
        ws.cell(row=row_num, column=1).border = border  # Add border to the row number column
        for col_num, cell in enumerate(row, 2):
            excel_cell = ws.cell(row=row_num, column=col_num, value=str(cell))
            excel_cell.alignment = Alignment(horizontal='center', vertical='center')
            excel_cell.border = border

        # Apply row color
        if row_num % 2 == 0:
            for col_num in range(1, len(headers) + 1):
                ws.cell(row=row_num, column=col_num).fill = PatternFill(start_color='E6E6E6', end_color='E6E6E6',
                                                                        fill_type='solid')  # Light gray
        else:
            for col_num in range(1, len(headers) + 1):
                ws.cell(row=row_num, column=col_num).fill = PatternFill(start_color='FFFFFF', end_color='FFFFFF',
                                                                        fill_type='solid')  # White

    # Auto-size columns
    for col_num, column in enumerate(ws.columns, 1):
        max_length = 0
        for cell in column:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(cell.value)
            except:
                pass
        adjusted_width = (max_length + 2) * 1.2
        ws.column_dimensions[get_column_letter(col_num)].width = adjusted_width

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=recent_rain.xlsx'
    wb.save(response)

    return response


@login_required
def rain_gauges_export_lat_long_xls(request):
    today = timezone.now()
    yesterday = today - datetime.timedelta(days=1)
    recent_rain = Station.objects.filter(last_rainfall_date_time__date__gte=yesterday).order_by('-recent_rainfall')
    table = RecentRainGaugeLatLongTable(recent_rain)
    RequestConfig(request).configure(table)

    wb = openpyxl.Workbook()
    ws = wb.active

    # Set right-to-left direction
    ws.sheet_view.rightToLeft = True

    # Write table headers
    headers = ['ردیف', 'شهرستان', 'نام', 'عرض ج', 'طول ج', 'مقدار بارندگی (میلیمتر)', 'زمان ثبت بارش']
    header_font = Font(bold=True, size=12, color='000000')
    header_fill = PatternFill(start_color='D3D3D3', end_color='D3D3D3', fill_type='solid')
    border = Border(left=Side(style='thin'), right=Side(style='thin'), top=Side(style='thin'),
                    bottom=Side(style='thin'))

    for col_num, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col_num, value=header)
        cell.font = header_font
        cell.alignment = Alignment(horizontal='center', vertical='center')
        cell.border = border

    # Write table rows
    row_color = 'FFFFFF'  # Start with a white color for the first row
    for row_num, row in enumerate(table.rows, 2):
        ws.cell(row=row_num, column=1, value=row_num - 1).alignment = Alignment(horizontal='center', vertical='center')
        ws.cell(row=row_num, column=1).border = border  # Add border to the row number column
        for col_num, cell in enumerate(row, 2):
            excel_cell = ws.cell(row=row_num, column=col_num, value=str(cell))
            excel_cell.alignment = Alignment(horizontal='center', vertical='center')
            excel_cell.border = border

        # Apply row color
        if row_num % 2 == 0:
            for col_num in range(1, len(headers) + 1):
                ws.cell(row=row_num, column=col_num).fill = PatternFill(start_color='E6E6E6', end_color='E6E6E6',
                                                                        fill_type='solid')  # Light gray
        else:
            for col_num in range(1, len(headers) + 1):
                ws.cell(row=row_num, column=col_num).fill = PatternFill(start_color='FFFFFF', end_color='FFFFFF',
                                                                        fill_type='solid')  # White

    # Auto-size columns
    for col_num, column in enumerate(ws.columns, 1):
        max_length = 0
        for cell in column:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(cell.value)
            except:
                pass
        adjusted_width = (max_length + 2) * 1.2
        ws.column_dimensions[get_column_letter(col_num)].width = adjusted_width

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=recent_rain_lat_long.xlsx'
    wb.save(response)

    return response



def get_color(recent_rainfall):
    if recent_rainfall < 5:
        return 'yellow'
    elif 5 <= recent_rainfall < 10:
        return 'orange'
    elif 10 <= recent_rainfall < 30:
        return 'lightgreen'
    elif 30 <= recent_rainfall < 50:
        return 'green'
    elif 50 <= recent_rainfall < 80:
        return 'blue'
    else:
        return 'red'


def recent_rain_gauge(request):
    today = timezone.now()
    yesterday = today - datetime.timedelta(days=1)

    # Filter stations with recent rainfall and exclude those without coordinates
    recent_rain_stations = Station.objects.filter(
        last_rainfall_date_time__date__gte=yesterday
    ).exclude(longitude=None, latitude=None)

    # Create a map centered on Fars province
    m = folium.Map(location=[29.1044, 53.0454], zoom_start=7)  # Fars province coordinates

    # Load GeoJSON data for cities of Fars province borders
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    with open(os.path.join(BASE_DIR, 'geojson_files', 'FarsCity.json'), 'r') as f:
        geojson_data = json.load(f)

    # Add GeoJSON layer to map
    folium.GeoJson(
        geojson_data,
        style_function=lambda feature: {
            'fillColor': '#ffffff00',  # Keep fill color transparent
            'color': 'gray',  # Use a different color for city borders, e.g., a shade of blue
            'weight': 2,  # Adjust border width for cities to be less than province borders
            'fillOpacity': 0.7,  # Adjust fill opacity as needed
        }
    ).add_to(m)

    # Load GeoJSON data for Fars province borders
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    with open(os.path.join(BASE_DIR, 'geojson_files', 'Fars.json'), 'r') as f:
        geojson_data = json.load(f)

    # Add GeoJSON layer to map
    folium.GeoJson(
        geojson_data,
        style_function=lambda feature: {
            'fillColor': '#ffffff00',  # Transparent fill color
            'color': 'black',  # Border color
            'weight': 3,  # Border width
            'fillOpacity': 0.5,
        }
    ).add_to(m)

    # Add markers for stations with recent rainfall
    for station in recent_rain_stations:
        if station.recent_rainfall > 0:  # Check if rainfall is greater than zero
            color = get_color(station.recent_rainfall)

            folium.Marker(
                [station.latitude, station.longitude],
                popup=f"{station.title} - بارندگی اخیر: {station.recent_rainfall} میلیمتر",
                icon=folium.Icon(color=color, icon='cloud')
            ).add_to(m)

    # Convert folium map to HTML string
    map_html = m._repr_html_()

    # Fetch recent rainfall data for table
    recent_rain = Station.objects.filter(
        last_rainfall_date_time__date__gte=yesterday
    ).order_by('-recent_rainfall')

    # Create and configure table
    table = RecentRainGaugeTable(recent_rain)
    RequestConfig(request).configure(table)

    allowed_users = ['mosein', '2450451331']


    return render(request, 'station_module/recent_rain_gauge.html',
                  {'table': table, 'today': today, 'map_html': map_html, 'allowed_users': allowed_users})


def table_update_rainfall(request):
    current_user = request.user
    workplace_code = None
    if hasattr(current_user, 'employee'):
        workplace_code = current_user.employee.workplace_code

    stations = Station.objects.filter(parent_station__code__exact=workplace_code, code__gte=19000, code__lte=99999)

    if request.method == 'POST':
        for station in stations:
            # دریافت مقادیر از فرم با استفاده از شناسه ایستگاه
            rainfall_3h = request.POST.get(f'rainfall_3h_{station.id}', '').strip()
            recent_rainfall = request.POST.get(f'recent_rainfall_{station.id}', '').strip()
            year_rainfall = request.POST.get(f'year_rainfall_{station.id}', '').strip()

            # تبدیل مقادیر دریافتی به float و بررسی اینکه آیا مقدار خالی یا منفی نباشد
            try:
                if rainfall_3h and float(rainfall_3h) >= 0:
                    station.rainfall_3h = float(rainfall_3h)
                if recent_rainfall and float(recent_rainfall) >= 0:
                    station.recent_rainfall = float(recent_rainfall)
                if year_rainfall and float(year_rainfall) >= 0:
                    station.year_rainfall = float(year_rainfall)

                # اگر حداقل یکی از فیلدها مقدار دارد، مدل را ذخیره کنید
                if rainfall_3h or recent_rainfall or year_rainfall:
                    station.save()
            except ValueError:
                # اگر مقدار نمی‌تواند به float تبدیل شود یا منفی است، خطا را مدیریت کنید
                pass

    return render(request, 'station_module/table_update_rainfall.html', {'stations': stations})


def stations_table_3h_recent_rainfall(request):
    # تعریف زمان‌های امروز و دیروز
    today = timezone.now()
    yesterday = today - datetime.timedelta(days=1)

    # ایجاد کوئری با استفاده از Q objects برای ترکیب شرایط
    stations = Station.objects.filter(
        Q(last_rainfall_date_time__date__gte=yesterday) &
        Q(code__gte=19000, code__lte=99999)
    ).order_by('-recent_rainfall')

    # اگر درخواست برای دانلود فایل اکسل باشد
    if 'download' in request.GET:
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="stations.xlsx"'

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Stations"

        # تنظیم جهت صفحه از راست به چپ
        ws.sheet_view.rightToLeft = True

        # نوشتن سربرگ‌های جدول
        columns = ['ردیف', 'نام ایستگاه', 'بارندگی 3 ساعته', 'جمع بارندگی سامانه اخیر (میلیمتر)', 'جمع بارندگی سال زرعی تا کنون (میلیمتر)']
        header_font = Font(bold=True, size=12, color='000000')
        header_fill = PatternFill(start_color='D3D3D3', end_color='D3D3D3', fill_type='solid')
        border = Border(left=Side(style='thin'), right=Side(style='thin'), top=Side(style='thin'),
                        bottom=Side(style='thin'))

        for col_num, column_title in enumerate(columns, 1):
            cell = ws.cell(row=1, column=col_num, value=column_title)
            cell.font = header_font
            cell.alignment = Alignment(horizontal='center', vertical='center')
            cell.border = border

        # نوشتن سطرهای جدول
        for row_num, station in enumerate(stations, 2):
            ws.cell(row=row_num, column=1, value=row_num - 1).alignment = Alignment(horizontal='center',
                                                                                    vertical='center')
            ws.cell(row=row_num, column=1).border = border
            ws.cell(row=row_num, column=2, value=station.title).alignment = Alignment(horizontal='center',
                                                                                      vertical='center')
            ws.cell(row=row_num, column=2).border = border
            ws.cell(row=row_num, column=3, value=station.rainfall_3h).alignment = Alignment(horizontal='center',
                                                                                            vertical='center')
            ws.cell(row=row_num, column=3).border = border
            ws.cell(row=row_num, column=4, value=station.recent_rainfall).alignment = Alignment(horizontal='center',
                                                                                                vertical='center')
            ws.cell(row=row_num, column=4).border = border
            ws.cell(row=row_num, column=5, value=station.year_rainfall).alignment = Alignment(horizontal='center',
                                                                                              vertical='center')
            ws.cell(row=row_num, column=5).border = border
            # ...

            # اعمال رنگ سطر
            row_fill = PatternFill(start_color='FFFFFF' if row_num % 2 == 1 else 'E6E6E6', end_color='FFFFFF' if row_num % 2 == 1 else 'E6E6E6', fill_type='solid')
            for col_num in range(1, len(columns) + 1):
                ws.cell(row=row_num, column=col_num).fill = row_fill

        # تنظیم اندازه خودکار ستون‌ها
        for col_num, column in enumerate(ws.columns, 1):
            max_length = max(len(str(cell.value)) for cell in column)
            adjusted_width = (max_length + 0) * 1.0
            ws.column_dimensions[get_column_letter(col_num)].width = adjusted_width

        wb.save(response)
        return response

    # اگر درخواست برای نمایش صفحه باشد
    return render(request, 'station_module/stations_table_3h_recent_rainfall.html', {'stations': stations})



