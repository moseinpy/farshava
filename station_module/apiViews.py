# from django.http import JsonResponse
# from django.views.decorators.csrf import csrf_exempt
#
#
# @csrf_exempt
# def save_rain_gauges(request):
#
#     id = request.POST.get('id', '')
#     type = request.POST.get('type', '')
#     value = request.POST.get('value', '')
#     rain_gauge = RainGauge.objects.get(id=id)
#
#     if type == "recent_rainfall":
#         rain_gauge.recent_rainfall = value
#
#     rain_gauge.save()
#     return JsonResponse({"success": "Updated"})