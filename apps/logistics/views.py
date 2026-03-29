from django.shortcuts import redirect
from django.http import JsonResponse
from django.contrib import messages
from .models import City, District


def set_city(request):
    """Teslimat şehri/ilçesi seç (session'a kaydet)."""
    if request.method == 'POST':
        city_id = request.POST.get('city_id')
        district_id = request.POST.get('district_id')

        try:
            city = City.objects.get(pk=city_id)
            request.session['city_id'] = city.pk

            if district_id:
                district = District.objects.get(pk=district_id, city=city)
                request.session['district_id'] = district.pk
            else:
                request.session.pop('district_id', None)

        except (City.DoesNotExist, District.DoesNotExist):
            messages.error(request, 'Geçersiz il/ilçe seçimi.')

    # AJAX response
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True})

    next_url = request.POST.get('next', request.META.get('HTTP_REFERER', '/'))
    return redirect(next_url)


def get_districts(request, city_id):
    """İlçe listesi döndür (AJAX)."""
    try:
        city = City.objects.get(pk=city_id)
        districts = list(city.districts.values('id', 'name').order_by('name'))
        return JsonResponse({'districts': districts})
    except City.DoesNotExist:
        return JsonResponse({'districts': []})
