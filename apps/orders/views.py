from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from apps.products.models import Product
from core.pricing import calculate_display_price, validate_quantity


def cart_view(request):
    """Sepet sayfası."""
    cart = request.session.get('cart', {})
    cart_items = []
    total = 0

    from apps.logistics.models import City
    city_id = request.session.get('city_id')
    city = None
    if city_id:
        try:
            city = City.objects.get(pk=city_id)
        except City.DoesNotExist:
            pass

    user = request.user if request.user.is_authenticated else None

    for product_id, item in cart.items():
        try:
            product = Product.objects.get(pk=int(product_id), is_active=True)
            mode = item.get('mode', 'ADET')
            quantity = item.get('quantity', 1)
            price = calculate_display_price(product, mode, user, city, quantity)
            cart_items.append({
                'product': product,
                'quantity': quantity,
                'mode': mode,
                'price': price,
            })
            total += price['total']
        except Product.DoesNotExist:
            continue

    return render(request, 'storefront/cart.html', {
        'cart_items': cart_items,
        'cart_total': total,
    })


def add_to_cart(request, product_id):
    """Sepete ürün ekle."""
    if request.method == 'POST':
        product = get_object_or_404(Product, pk=product_id, is_active=True)
        mode = request.POST.get('mode', 'ADET')
        try:
            quantity = int(request.POST.get('quantity', product.min_order_adet))
        except (ValueError, TypeError):
            quantity = product.min_order_adet

        # Misafir: sadece ADET
        if not request.user.is_authenticated:
            mode = 'ADET'

        # Miktar doğrula
        is_valid, corrected_qty, error_msg = validate_quantity(product, mode, quantity)
        if not is_valid:
            messages.warning(request, error_msg)
            quantity = corrected_qty

        cart = request.session.get('cart', {})
        cart[str(product_id)] = {
            'quantity': quantity,
            'mode': mode,
        }
        request.session['cart'] = cart
        request.session.modified = True

        messages.success(request, f'{product.name} sepete eklendi!')

    return redirect('products:detail', slug=product.slug)


def update_cart(request, product_id):
    """Sepet miktarı güncelle."""
    if request.method == 'POST':
        cart = request.session.get('cart', {})
        key = str(product_id)
        if key in cart:
            try:
                quantity = int(request.POST.get('quantity', 1))
                cart[key]['quantity'] = max(1, quantity)
                request.session['cart'] = cart
                request.session.modified = True
            except (ValueError, TypeError):
                pass
    return redirect('orders:cart')


def remove_from_cart(request, product_id):
    """Sepetten ürün çıkar."""
    cart = request.session.get('cart', {})
    key = str(product_id)
    if key in cart:
        del cart[key]
        request.session['cart'] = cart
        request.session.modified = True
        messages.info(request, 'Ürün sepetten çıkarıldı.')
    return redirect('orders:cart')


@login_required
def order_list(request):
    """Sipariş listesi."""
    orders = request.user.orders.all()
    return render(request, 'storefront/order_list.html', {
        'orders': orders,
    })
