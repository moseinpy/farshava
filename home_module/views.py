from django.db.models import Count
from django.shortcuts import render
from django.views.generic import TemplateView
from station_module.models import Station, StationCategory
from utils.convertors import group_list
from site_module.models import SiteSetting, FooterLinkBox, Slider, SiteBanner
from datetime import date, timedelta
from jalali_date import date2jalali




class HomeView(TemplateView):
    template_name = 'home_module/index_page.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        sliders = Slider.objects.filter(is_active=True)
        context['sliders'] = sliders
        main_synoptic_stations = Station.objects.filter(category__url_title__iexact='main-synoptic').filter(
            is_active=True, is_delete=False).order_by('-id')
        additional_synoptic_stations = Station.objects.filter(category__url_title__iexact='additional-synoptic').filter(
            is_active=True, is_delete=False).order_by('-id')
        climatology_stations = Station.objects.filter(category__url_title__iexact='climatology').filter(is_active=True, is_delete=False).order_by('-id')
        day = date2jalali(date.today() - timedelta(0)).strftime('%Y%m%d')
        # tahlil = f'https://www.farsmet.ir/DM/Files/files/tahlil{day}.pdf'
        # vaziat = f'https://www.farsmet.ir/DM/Files/files/vaziat{day}.png'
        # context['tahlil'] = tahlil
        # context['vaziat'] = vaziat
        context['main_synoptic_stations'] = group_list(main_synoptic_stations)
        context['additional_synoptic_stations'] = group_list(additional_synoptic_stations)
        context['climatology_stations'] = group_list(climatology_stations)
        categories = list(
            StationCategory.objects.annotate(station_count=Count('station_categories')).filter(is_active=True,
                                                                                               is_delete=False,
                                                                                               station_count__gt=0)[:6])
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
        'footer_link_boxes': footer_link_boxes,
    }
    return render(request, 'shared/site_footer_component.html', context)


# def site_footer_component(request):
#     setting: SiteSetting = SiteSetting.objects.filter(is_main_setting=True).first()
#     footer_link_boxes = FooterLinkBox.objects.all()
#     context = {
#         'site_setting': setting,
#         'footer_link_boxes': footer_link_boxes
#     }
#     return render(request, 'shared/site_footer_component.html', context)


class AboutView(TemplateView):
    template_name = 'home_module/about_page.html'

    def get_context_data(self, **kwargs):
        context = super(AboutView, self).get_context_data(**kwargs)
        site_setting: SiteSetting = SiteSetting.objects.filter(is_main_setting=True).first()
        context['site_setting'] = site_setting
        return context
