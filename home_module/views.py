from django.db.models import Count
from django.shortcuts import render
from django.views.generic import TemplateView
from station_module.models import Station, StationCategory
from utils.convertors import group_list
from site_module.models import SiteSetting, FooterLinkBox, Slider, SiteBanner


class HomeView(TemplateView):
    template_name = 'home_module/index_page.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        sliders = Slider.objects.filter(is_active=True)
        context['sliders'] = sliders
        latest_stations = Station.objects.exclude(category__url_title__iexact='rain-gauge').filter(is_active=True, is_delete=False).order_by('-id')[:12]
        most_visit_stations = Station.objects.exclude(category__url_title__iexact='rain-gauge').filter(is_active=True, is_delete=False).annotate(
            visit_count=Count('stationvisit')).order_by('-visit_count')[:4]
        context['latest_stations'] = group_list(latest_stations)
        context['most_visit_stations'] = group_list(most_visit_stations)
        categories = list(StationCategory.objects.annotate(station_count=Count('station_categories')).filter(is_active=True, is_delete=False, station_count__gt=0)[:6])
        categories_stations = []

        for category in categories:
            item = {
                'id': category.id,
                'title': category.title,
                'products': list(category.station_categories.all()[:4])
            }
            categories_stations.append(item)
        context['categories_stations'] = categories_stations

        return context


def site_header_component(request):
    setting: SiteSetting = SiteSetting.objects.filter(is_main_setting=True).first()
    context = {
        'site_setting': setting
    }
    return render(request, 'shared/site_header_component.html', context)


def site_footer_component(request):
    setting: SiteSetting = SiteSetting.objects.filter(is_main_setting=True).first()
    footer_link_boxes = FooterLinkBox.objects.all()
    context = {
        'site_setting': setting,
        'footer_link_boxes': footer_link_boxes
    }
    return render(request, 'shared/site_footer_component.html', context)


class AboutView(TemplateView):
    template_name = 'home_module/about_page.html'

    def get_context_data(self, **kwargs):
        context = super(AboutView, self).get_context_data(**kwargs)
        site_setting: SiteSetting = SiteSetting.objects.filter(is_main_setting=True).first()
        context['site_setting'] = site_setting
        return context

