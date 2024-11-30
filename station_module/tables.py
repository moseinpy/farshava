import django_tables2 as tables
from .models import Station
from jalali_date import datetime2jalali


class RecentRainGaugeTable(tables.Table):
    row_number = tables.Column(empty_values=(), verbose_name='ردیف', attrs={
        'th': {'class': 'text-center font-weight-bold column-row-number'},
        'td': {'class': 'text-center font-weight-bold column-row-number'}
    })

    city = tables.Column(verbose_name='شهرستان', attrs={'th': {'class': 'text-center font-weight-bold column-city'},
                                                        'td': {'class': 'text-center font-weight-bold column-city'}},
                         orderable=True)
    title = tables.Column(verbose_name='نام ایستگاه',
                          attrs={'th': {'class': 'text-center font-weight-bold column-title'},
                                 'td': {'class': 'text-center font-weight-bold column-title'}},
                          orderable=True)
    recent_rainfall = tables.Column(verbose_name='بارندگی اخیر',
                                    attrs={'th': {'class': 'text-center font-weight-bold column-recent-rainfall'},
                                           'td': {
                                               'class': 'text-center font-weight-bold column-recent-rainfall'}},
                                    orderable=True)
    last_rainfall_date_time = tables.Column(verbose_name='تاریخ و ساعت ثبت بارش',
                                            attrs={'th': {
                                                'class': 'text-center font-weight-bold column-last-rainfall-date-time'},
                                                'td': {
                                                    'class': 'text-center font-weight-bold column-last-rainfall-date-time'}},
                                            orderable=True)

    def render_row_number(self):
        # شمارش ردیف ها از 1 شروع می شود
        return f"{self.row_counter}"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.row_counter = 1

    def on_bind_field(self, field, column):
        super().on_bind_field(field, column)
        if column.name == "row_number":
            self.row_counter += 1

    def render_last_rainfall_date_time(self, value):
        if value is None:
            return ''
        else:
            return datetime2jalali(value).strftime('%H:%M:%S - %Y/%m/%d')
            # jalali_date = date2jalali(value)
            # return f"{value.hour}:{value.minute} ** {jalali_date.year}/{jalali_date.month}/{jalali_date.day}"

    class Meta:
        model = Station
        template_name = 'django_tables2/bootstrap4.html'
        fields = ['city', 'title', 'recent_rainfall']
        sequence = ('row_number', 'city', 'title', 'recent_rainfall', 'last_rainfall_date_time')  # ترتیب ستون‌ها
        attrs = {'class': 'table table-striped table-hover table-bordered table-sm'}


class RecentRainGaugeLatLongTable(tables.Table):
    city = tables.Column(verbose_name='شهرستان', attrs={'th': {'class': 'text-center font-weight-bold'},
                                                        'td': {'class': 'text-center font-weight-bold'}},
                         orderable=True)
    title = tables.Column(verbose_name='نام ایستگاه', attrs={'th': {'class': 'text-center font-weight-bold'},
                                                             'td': {'class': 'text-center font-weight-bold'}},
                          orderable=True)
    latitude = tables.Column(verbose_name='عرض ج', attrs={'th': {'class': 'text-center font-weight-bold'},
                                                          'td': {'class': 'text-center font-weight-bold'}},
                             orderable=True)
    longitude = tables.Column(verbose_name='طول ج', attrs={'th': {'class': 'text-center font-weight-bold'},
                                                           'td': {'class': 'text-center font-weight-bold'}},
                              orderable=True)
    recent_rainfall = tables.Column(verbose_name='بارندگی اخیر', attrs={'th': {'class': 'text-center font-weight-bold'},
                                                                        'td': {
                                                                            'class': 'text-center font-weight-bold'}},
                                    orderable=True)
    last_rainfall_date_time = tables.Column(verbose_name='تاریخ و ساعت ثبت بارش',
                                            attrs={'th': {'class': 'text-center font-weight-bold'},
                                                   'td': {'class': 'text-center font-weight-bold'}}, orderable=True)

    def render_last_rainfall_date_time(self, value):
        if value is None:
            return ''
        else:
            return datetime2jalali(value).strftime('%H:%M:%S - %Y/%m/%d')
            # jalali_date = date2jalali(value)
            # return f"{value.hour}:{value.minute} ** {jalali_date.year}/{jalali_date.month}/{jalali_date.day}"

    class Meta:
        model = Station
        template_name = 'django_tables2/bootstrap4.html'
        fields = ['city', 'title', 'latitude', 'longitude', 'recent_rainfall']
        attrs = {'class': 'table table-striped table-hover table-bordered table-sm'}


class Rainfall24hTable(tables.Table):
    row_number = tables.Column(
        empty_values=(),
        verbose_name="ردیف",
        orderable=False,
        attrs={'th': {'class': 'text-center column-row-number unique-row-number'},
               'td': {'class': 'text-center unique-row-number'}}
    )
    city = tables.Column(
        verbose_name="شهرستان",
        orderable=True,
        attrs={'th': {'class': 'text-center column-city unique-city'}, 'td': {'class': 'text-center unique-city'}}
    )
    title = tables.Column(
        verbose_name="ایستگاه",
        orderable=True,
        attrs={'th': {'class': 'text-center column-title unique-title'}, 'td': {'class': 'text-center unique-title'}}
    )
    rainfall_24h = tables.Column(
        verbose_name="24 ساعته",
        orderable=True,
        attrs={'th': {'class': 'text-center column-rainfall unique-rainfall-24h'},
               'td': {'class': 'text-center unique-rainfall-24h'}}
    )
    recent_rainfall = tables.Column(
        verbose_name="اخیر",
        orderable=True,
        attrs={'th': {'class': 'text-center column-recent-rainfall unique-recent-rainfall'},
               'td': {'class': 'text-center unique-recent-rainfall'}}
    )
    year_rainfall = tables.Column(
        verbose_name="سال آبی",
        orderable=True,
        attrs={'th': {'class': 'text-center column-year-rainfall unique-year-rainfall'},
               'td': {'class': 'text-center unique-year-rainfall'}}
    )
    last_rainfall_date_time = tables.Column(
        verbose_name="تاریخ و ساعت ثبت",
        orderable=True,
        attrs={'th': {'class': 'text-center column-last-date-time unique-last-date-time'},
               'td': {'class': 'text-center unique-last-date-time'}}
    )

    def render_row_number(self, *args, **kwargs):
        self.counter += 1  # افزایش شمارنده
        return self.counter

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.counter = 0  # مقدار اولیه شمارنده

    def render_last_rainfall_date_time(self, value):
        if value is None:
            return ''
        else:
            return datetime2jalali(value).strftime('%H:%M:%S - %Y/%m/%d')

    class Meta:
        model = Station
        template_name = 'django_tables2/bootstrap4.html'
        fields = ['city', 'title', 'rainfall_24h', 'recent_rainfall', 'year_rainfall', 'last_rainfall_date_time']
        sequence = ('row_number', 'city', 'title', 'rainfall_24h', 'recent_rainfall', 'year_rainfall',
                    'last_rainfall_date_time')  # ترتیب ستون‌ها
        order_by = '-recent_rainfall'  # مرتب‌سازی پیش‌فرض جدول

        attrs = {
            'class': 'table table-bordered table-striped table-sm',
            'thead': {'class': 'thead-light'},
        }
