"""Global template context processors."""


def global_context(request):
    """Tüm template'lere genel veriler ekle."""
    from apps.products.models import Category
    from apps.logistics.models import City

    # Sepet bilgisi (session bazlı)
    cart = request.session.get('cart', {})
    cart_count = sum(item.get('quantity', 0) for item in cart.values()) if cart else 0

    # Teslimat şehri
    city_id = request.session.get('city_id')
    district_id = request.session.get('district_id')
    selected_city = None
    selected_district = None

    if city_id:
        try:
            selected_city = City.objects.get(pk=city_id)
        except City.DoesNotExist:
            pass

    if district_id:
        from apps.logistics.models import District
        try:
            selected_district = District.objects.get(pk=district_id)
        except District.DoesNotExist:
            pass

    return {
        'all_categories': Category.objects.filter(is_active=True).order_by('order', 'name'),
        'cart_count': cart_count,
        'selected_city': selected_city,
        'selected_district': selected_district,
        'location_selected': selected_city is not None,
    }
