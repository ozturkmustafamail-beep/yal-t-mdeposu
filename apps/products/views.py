from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import Product, Category, Brand
from core.pricing import calculate_display_price, validate_quantity


def home(request):
    """Ana sayfa."""
    featured_products = Product.objects.filter(
        is_active=True, is_featured=True
    ).select_related('category', 'brand')[:8]

    categories = Category.objects.filter(is_active=True)

    # Fiyat hesapla
    from apps.logistics.models import City
    city_id = request.session.get('city_id')
    city = None
    if city_id:
        try:
            city = City.objects.get(pk=city_id)
        except City.DoesNotExist:
            pass

    products_with_prices = []
    for product in featured_products:
        user = request.user if request.user.is_authenticated else None
        price_info = calculate_display_price(product, 'ADET', user, city)
        products_with_prices.append({
            'product': product,
            'price': price_info,
        })

    return render(request, 'storefront/home.html', {
        'featured_products': products_with_prices,
        'categories': categories,
    })


def product_list(request):
    """Ürün listeleme sayfası."""
    products = Product.objects.filter(is_active=True).select_related('category', 'brand')

    # Filtreler
    category_slug = request.GET.get('category')
    brand_slug = request.GET.get('brand')
    search = request.GET.get('q')

    if category_slug:
        products = products.filter(category__slug=category_slug)
    if brand_slug:
        products = products.filter(brand__slug=brand_slug)
    if search:
        products = products.filter(name__icontains=search)

    # Şehir
    from apps.logistics.models import City
    city_id = request.session.get('city_id')
    city = None
    if city_id:
        try:
            city = City.objects.get(pk=city_id)
        except City.DoesNotExist:
            pass

    user = request.user if request.user.is_authenticated else None

    products_with_prices = []
    for product in products:
        price_info = calculate_display_price(product, 'ADET', user, city)
        products_with_prices.append({
            'product': product,
            'price': price_info,
        })

    categories = Category.objects.filter(is_active=True)
    brands = Brand.objects.filter(is_active=True)
    selected_category = None
    if category_slug:
        selected_category = Category.objects.filter(slug=category_slug).first()

    return render(request, 'storefront/product_list.html', {
        'products_with_prices': products_with_prices,
        'categories': categories,
        'brands': brands,
        'selected_category': selected_category,
        'selected_brand': brand_slug,
        'search_query': search or '',
    })


def product_detail(request, slug):
    """Ürün detay sayfası."""
    product = get_object_or_404(Product, slug=slug, is_active=True)

    from apps.logistics.models import City
    city_id = request.session.get('city_id')
    city = None
    if city_id:
        try:
            city = City.objects.get(pk=city_id)
        except City.DoesNotExist:
            pass

    mode = request.GET.get('mode', 'ADET')
    user = request.user if request.user.is_authenticated else None

    # Misafir: sadece ADET
    if not request.user.is_authenticated and mode != 'ADET':
        mode = 'ADET'

    quantity = 1
    if mode == 'PALET' and product.has_palet:
        quantity = product.palet_quantity
    elif mode == 'TIR' and product.has_tir:
        quantity = product.tir_quantity
    else:
        quantity = product.min_order_adet

    price_info = calculate_display_price(product, mode, user, city, quantity)

    # Tüm modlar için fiyat bilgisi
    all_prices = {'ADET': calculate_display_price(product, 'ADET', user, city)}
    if product.has_palet and request.user.is_authenticated:
        all_prices['PALET'] = calculate_display_price(product, 'PALET', user, city, product.palet_quantity)
    if product.has_tir and request.user.is_authenticated:
        all_prices['TIR'] = calculate_display_price(product, 'TIR', user, city, product.tir_quantity)

    return render(request, 'storefront/product_detail.html', {
        'product': product,
        'price': price_info,
        'all_prices': all_prices,
        'current_mode': mode,
        'quantity': quantity,
    })


def product_price_api(request, pk):
    """AJAX endpoint - dinamik fiyat hesaplama."""
    product = get_object_or_404(Product, pk=pk, is_active=True)

    mode = request.GET.get('mode', 'ADET')
    try:
        quantity = int(request.GET.get('quantity', 1))
    except (ValueError, TypeError):
        quantity = 1

    from apps.logistics.models import City
    city_id = request.session.get('city_id')
    city = None
    if city_id:
        try:
            city = City.objects.get(pk=city_id)
        except City.DoesNotExist:
            pass

    # Miktar doğrulama
    is_valid, corrected_qty, error_msg = validate_quantity(product, mode, quantity)
    user = request.user if request.user.is_authenticated else None
    price_info = calculate_display_price(product, mode, user, city, corrected_qty)

    return JsonResponse({
        'unit_price': str(price_info['unit_price']),
        'original_price': str(price_info['original_price']),
        'shipping_per_unit': str(price_info['shipping_per_unit']),
        'kdv_amount': str(price_info['kdv_amount']),
        'ambar_fee': str(price_info['ambar_fee']),
        'ambar_note': price_info['ambar_note'],
        'quantity': corrected_qty,
        'subtotal': str(price_info['subtotal']),
        'discount': str(price_info['discount']),
        'total': str(price_info['total']),
        'mode': mode,
        'kdv_included': price_info['kdv_included'],
        'shipping_included': price_info['shipping_included'],
        'is_valid': is_valid,
        'error_msg': error_msg,
        'is_plus_discount': price_info['is_plus_discount'],
    })
