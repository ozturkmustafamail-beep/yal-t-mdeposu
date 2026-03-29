"""
Fiyatlandırma Motoru — Yalitimdeposu.com

Fiyat Kuralları:
┌──────────┬───────────────┬──────────────┬────────────────┐
│ Mod      │ KDV           │ Nakliye      │ Görünürlük     │
├──────────┼───────────────┼──────────────┼────────────────┤
│ ADET     │ Dahil         │ Dahil        │ Herkes         │
│ PALET    │ Hariç         │ Hariç        │ Sadece üye     │
│ TIR      │ Hariç         │ Hariç        │ Sadece üye     │
└──────────┴───────────────┴──────────────┴────────────────┘

Plus İndirim: %3 tüm ürünlere (tek seferde 10.000 TL+ sipariş sonrası 1 ay)
"""
from decimal import Decimal
from django.conf import settings


def get_shipping_cost(product, city=None):
    """
    Ürünün ağırlık/ebadına göre nakliye maliyeti hesapla.
    Marmara bölgesi baz alınarak KDV dahil fiyat üretir.
    """
    from apps.logistics.models import ShippingTariff

    if not city and not product.weight_kg:
        return Decimal('0.00')

    # Ücretlendirilebilir ağırlık
    chargeable = product.chargeable_weight or Decimal('1')

    # Önce şehir bazlı tarife ara
    tariff = None
    if city:
        tariff = ShippingTariff.objects.filter(
            city=city, is_active=True
        ).first()

    # Sonra bölge bazlı
    if not tariff and city and city.region:
        tariff = ShippingTariff.objects.filter(
            region=city.region, city__isnull=True, is_active=True
        ).first()

    # Genel tarife
    if not tariff:
        tariff = ShippingTariff.objects.filter(
            region='', city__isnull=True, is_active=True
        ).first()

    if not tariff:
        return Decimal('0.00')

    if tariff.calc_type == 'per_kg':
        cost = chargeable * tariff.cost
    elif tariff.calc_type == 'per_desi':
        vol_weight = product.volumetric_weight or chargeable
        cost = vol_weight * tariff.cost
    else:  # per_unit
        cost = tariff.cost

    return max(cost, tariff.min_charge)


def get_ambar_fee(product, city=None):
    """Ambar (depolama) ücreti hesapla."""
    from apps.logistics.models import AmbarConfig

    if not city:
        return Decimal('0.00'), ''

    # Şehir bazlı ambar config
    config = AmbarConfig.objects.filter(city=city).first()
    if not config and city.region:
        config = AmbarConfig.objects.filter(region=city.region, city__isnull=True).first()
    if not config:
        config = AmbarConfig.objects.filter(region='', city__isnull=True).first()

    if not config:
        return Decimal('0.00'), ''

    weight = product.chargeable_weight or Decimal('1')
    fee = weight * config.estimated_fee_per_kg
    return fee, config.notes


def calculate_display_price(product, mode='ADET', user=None, city=None, quantity=1):
    """
    Kullanıcıya gösterilecek fiyat hesapla.

    Returns dict:
    {
        'unit_price': Decimal,         # Gösterilecek birim fiyat
        'original_price': Decimal,     # İndirim öncesi (Plus varsa)
        'shipping_per_unit': Decimal,  # Birim nakliye (adet modunda dahil)
        'kdv_amount': Decimal,         # KDV tutarı (bilgi amaçlı)
        'ambar_fee': Decimal,          # Ambar ücreti (bilgi amaçlı)
        'ambar_note': str,
        'subtotal': Decimal,
        'total': Decimal,
        'discount': Decimal,
        'discount_percent': int,
        'mode': str,
        'quantity': int,
        'kdv_included': bool,
        'shipping_included': bool,
        'is_plus_discount': bool,
    }
    """
    kdv_rate = Decimal(str(product.kdv_rate)) / Decimal('100')
    plus_discount = Decimal('0')
    is_plus = False

    # Plus kontrolü
    if user and hasattr(user, 'is_plus') and user.is_plus:
        is_plus = True
        plus_discount = Decimal(str(getattr(settings, 'PLUS_DISCOUNT_PERCENT', 3))) / Decimal('100')

    result = {
        'mode': mode,
        'quantity': quantity,
        'is_plus_discount': is_plus,
        'discount_percent': int(plus_discount * 100),
    }

    if mode == 'ADET':
        # KDV dahil, nakliye dahil
        unit_price = product.price_adet
        shipping = get_shipping_cost(product, city)
        ambar_fee, ambar_note = Decimal('0.00'), ''

        # KDV bilgi amaçlı (fiyatın içinde)
        kdv_amount = unit_price * kdv_rate / (1 + kdv_rate)

        result.update({
            'unit_price': unit_price,
            'original_price': unit_price,
            'shipping_per_unit': shipping,
            'kdv_amount': kdv_amount.quantize(Decimal('0.01')),
            'ambar_fee': ambar_fee,
            'ambar_note': ambar_note,
            'kdv_included': True,
            'shipping_included': True,
        })

    elif mode == 'PALET' and product.has_palet:
        # KDV hariç, nakliye hariç
        unit_price = product.price_palet
        ambar_fee, ambar_note = get_ambar_fee(product, city)
        kdv_amount = unit_price * kdv_rate  # bilgi amaçlı

        result.update({
            'unit_price': unit_price,
            'original_price': unit_price,
            'shipping_per_unit': Decimal('0.00'),
            'kdv_amount': kdv_amount.quantize(Decimal('0.01')),
            'ambar_fee': ambar_fee.quantize(Decimal('0.01')),
            'ambar_note': ambar_note,
            'kdv_included': False,
            'shipping_included': False,
        })

    elif mode == 'TIR' and product.has_tir:
        # KDV hariç, nakliye hariç
        unit_price = product.price_tir
        ambar_fee, ambar_note = get_ambar_fee(product, city)
        kdv_amount = unit_price * kdv_rate

        result.update({
            'unit_price': unit_price,
            'original_price': unit_price,
            'shipping_per_unit': Decimal('0.00'),
            'kdv_amount': kdv_amount.quantize(Decimal('0.01')),
            'ambar_fee': ambar_fee.quantize(Decimal('0.01')),
            'ambar_note': ambar_note,
            'kdv_included': False,
            'shipping_included': False,
        })
    else:
        # Fallback
        unit_price = product.price_adet
        result.update({
            'unit_price': unit_price,
            'original_price': unit_price,
            'shipping_per_unit': Decimal('0.00'),
            'kdv_amount': Decimal('0.00'),
            'ambar_fee': Decimal('0.00'),
            'ambar_note': '',
            'kdv_included': True,
            'shipping_included': True,
        })

    # Plus indirim uygula
    if is_plus:
        discount_amount = result['unit_price'] * plus_discount
        result['unit_price'] = (result['unit_price'] - discount_amount).quantize(Decimal('0.01'))
        result['discount'] = (discount_amount * quantity).quantize(Decimal('0.01'))
    else:
        result['discount'] = Decimal('0.00')

    # Toplamlar
    result['subtotal'] = (result['unit_price'] * quantity).quantize(Decimal('0.01'))
    result['total'] = result['subtotal'] + result.get('ambar_fee', Decimal('0.00'))

    return result


def validate_quantity(product, mode, quantity):
    """
    Miktar doğrula.
    Returns (is_valid, corrected_quantity, error_message)
    """
    if mode == 'ADET':
        min_qty = product.min_order_adet
        if quantity < min_qty:
            return False, min_qty, f'Minimum {min_qty} adet sipariş verebilirsiniz.'
        return True, quantity, ''

    elif mode == 'PALET':
        if not product.has_palet:
            return False, 0, 'Bu ürün palet olarak satılmamaktadır.'
        step = product.palet_quantity
        if quantity < step:
            return False, step, f'Palet bazında minimum {step} adet.'
        if quantity % step != 0:
            corrected = (quantity // step) * step
            if corrected < step:
                corrected = step
            return False, corrected, f'Palet katları halinde sipariş verilmelidir ({step}\'er adet).'
        return True, quantity, ''

    elif mode == 'TIR':
        if not product.has_tir:
            return False, 0, 'Bu ürün tır olarak satılmamaktadır.'
        step = product.tir_quantity
        if quantity < step:
            return False, step, f'Tır bazında minimum {step} adet.'
        if quantity % step != 0:
            corrected = (quantity // step) * step
            if corrected < step:
                corrected = step
            return False, corrected, f'Tır katları halinde sipariş verilmelidir ({step}\'er adet).'
        return True, quantity, ''

    return False, quantity, 'Geçersiz satış modu.'
