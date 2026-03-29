from django.db import models
from django.conf import settings
import uuid


class Order(models.Model):
    """Müşteri siparişi."""

    STATUS_CHOICES = [
        ('pending', 'Beklemede'),
        ('paid', 'Ödeme Alındı'),
        ('processing', 'Hazırlanıyor'),
        ('shipped', 'Sevk Edildi'),
        ('delivered', 'Teslim Edildi'),
        ('cancelled', 'İptal Edildi'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='orders', verbose_name='Kullanıcı',
        null=True, blank=True  # Misafir siparişi için
    )
    delivery_address = models.ForeignKey(
        'accounts.Address', on_delete=models.SET_NULL,
        null=True, blank=True, verbose_name='Teslimat Adresi'
    )
    # Misafir siparişleri için ayrı adres alanları
    guest_name = models.CharField(max_length=200, blank=True, verbose_name='Ad Soyad')
    guest_phone = models.CharField(max_length=20, blank=True, verbose_name='Telefon')
    guest_city = models.ForeignKey(
        'logistics.City', on_delete=models.SET_NULL,
        null=True, blank=True, verbose_name='İl'
    )
    guest_district = models.ForeignKey(
        'logistics.District', on_delete=models.SET_NULL,
        null=True, blank=True, verbose_name='İlçe'
    )
    guest_address = models.TextField(blank=True, verbose_name='Açık Adres')

    order_number = models.CharField(
        max_length=20, unique=True, verbose_name='Sipariş No'
    )
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES,
        default='pending', verbose_name='Durum'
    )

    subtotal = models.DecimalField(
        max_digits=12, decimal_places=2, default=0,
        verbose_name='Ara Toplam (TL)'
    )
    shipping_total = models.DecimalField(
        max_digits=10, decimal_places=2, default=0,
        verbose_name='Toplam Nakliye (TL)'
    )
    discount_amount = models.DecimalField(
        max_digits=10, decimal_places=2, default=0,
        verbose_name='İndirim Tutarı (TL)'
    )
    total = models.DecimalField(
        max_digits=12, decimal_places=2, default=0,
        verbose_name='Genel Toplam (TL)'
    )

    notes = models.TextField(blank=True, verbose_name='Sipariş Notları')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Sipariş'
        verbose_name_plural = 'Siparişler'
        ordering = ['-created_at']

    def __str__(self):
        return f"Sipariş #{self.order_number}"

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = f"YD-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

    def calculate_total(self):
        """Sipariş toplamını kalemlerden hesapla."""
        items = self.items.all()
        self.subtotal = sum(item.line_total for item in items)
        self.shipping_total = sum(item.shipping_cost for item in items)
        self.total = self.subtotal + self.shipping_total - self.discount_amount
        self.save(update_fields=['subtotal', 'shipping_total', 'total'])


class OrderItem(models.Model):
    """Sipariş kalemi."""

    SALE_MODE_CHOICES = [
        ('ADET', 'Adet'),
        ('PALET', 'Palet'),
        ('TIR', 'Tır'),
    ]

    order = models.ForeignKey(
        Order, on_delete=models.CASCADE,
        related_name='items', verbose_name='Sipariş'
    )
    product = models.ForeignKey(
        'products.Product', on_delete=models.CASCADE,
        verbose_name='Ürün'
    )
    sale_mode = models.CharField(
        max_length=10, choices=SALE_MODE_CHOICES,
        default='ADET', verbose_name='Satış Modu'
    )
    quantity = models.PositiveIntegerField(verbose_name='Miktar')
    unit_price = models.DecimalField(
        max_digits=10, decimal_places=2,
        verbose_name='Birim Fiyat (TL)'
    )
    shipping_cost = models.DecimalField(
        max_digits=10, decimal_places=2, default=0,
        verbose_name='Nakliye Maliyeti (TL)'
    )

    class Meta:
        verbose_name = 'Sipariş Kalemi'
        verbose_name_plural = 'Sipariş Kalemleri'

    def __str__(self):
        return f"{self.product.name} x{self.quantity} ({self.sale_mode})"

    @property
    def line_total(self):
        return self.unit_price * self.quantity
