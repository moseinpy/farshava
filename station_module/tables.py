import django_tables2 as tables
from .models import Station


class RecentRainGaugeTable(tables.Table):
    city = tables.Column(verbose_name='شهر', attrs={'th': {'class': 'text-center font-weight-bold'}, 'td': {'class': 'text-center font-weight-bold'}}, orderable=True)
    title = tables.Column(verbose_name='نام', attrs={'th': {'class': 'text-center font-weight-bold'}, 'td': {'class': 'text-center font-weight-bold'}}, orderable=True)
    recent_rainfall = tables.Column(verbose_name='بارندگی اخیر', attrs={'th': {'class': 'text-center font-weight-bold'}, 'td': {'class': 'text-center font-weight-bold'}}, orderable=True)

    class Meta:
        model = Station
        template_name = 'django_tables2/bootstrap4.html'
        fields = ['city', 'title', 'recent_rainfall']
        attrs = {'class': 'table table-striped table-hover table-bordered table-sm'}

