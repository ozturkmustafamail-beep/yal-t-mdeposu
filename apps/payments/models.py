from django.db import models


class POSProvider(models.Model):
    """
    Sanal POS sağlayıcı.
    - Adet siparişleri: Kendi şirket POS'u
    - Palet/Tır siparişleri: Fabrika POS'ları
    """
    PROVIDER_TYPE_CHOICES = [
        ('company', 'Şirket POS (Adet Siparişleri)'),
        ('factory', 'Fabrika POS (Toptan Siparişler)'),
    ]

    name = models.CharField(max_length=100, verbose_name='POS Adı')
    provider_type = models.CharField(
        max_length=20, choices=PROVIDER_TYPE_CHOICES,
        default='company', verbose_name='POS Tipi'
    )
    factory_name = models.CharField(
        max_length=200, blank=True, verbose_name='Fabrika Adı',
        help_text='Fabrika POS ise fabrika adı'
    )
    api_key = models.CharField(max_length=500, blank=True, verbose_name='API Key')
    api_secret = models.CharField(max_length=500, blank=True, verbose_name='API Secret')
    merchant_id = models.CharField(max_length=200, blank=True, verbose_name='Merchant ID')
    is_active = models.BooleanField(default=True, verbose_name='Aktif')

    # Taksit ayarları
    max_installments = models.PositiveIntegerField(
        default=1, verbose_name='Maksimum Taksit Sayısı'
    )
    installment_rates = models.JSONField(
        default=dict, blank=True,
        verbose_name='Taksit Oranları',
        help_text='{"2": 0, "3": 0, "6": 1.5, "9": 3.0, "12": 5.0}'
    )

    class Meta:
        verbose_name = 'Sanal POS'
        verbose_name_plural = 'Sanal POS\'lar'

    def __str__(self):
        return f"{self.name} ({self.get_provider_type_display()})"


class POSRouting(models.Model):
    """
    POS yönlendirme — Admin hangi POS'un aktif olduğunu belirler.
    
    Kurallar:
    - ADET siparişler → her zaman şirket POS'u
    - PALET/TIR siparişler → admin'in seçtiği aktif fabrika POS'u
    - Admin haftalık/dönemsel olarak fabrika POS'unu değiştirebilir
    """
    SALE_MODE_CHOICES = [
        ('ADET', 'Adet Siparişleri'),
        ('TOPTAN', 'Toptan Siparişler (Palet + Tır)'),
    ]

    sale_mode = models.CharField(
        max_length=10, choices=SALE_MODE_CHOICES,
        verbose_name='Satış Modu'
    )
    pos_provider = models.ForeignKey(
        POSProvider, on_delete=models.CASCADE,
        related_name='routings', verbose_name='POS Sağlayıcı'
    )
    is_active = models.BooleanField(default=True, verbose_name='Aktif')
    valid_from = models.DateTimeField(
        null=True, blank=True,
        verbose_name='Geçerlilik Başlangıcı'
    )
    valid_until = models.DateTimeField(
        null=True, blank=True,
        verbose_name='Geçerlilik Bitişi'
    )
    notes = models.TextField(
        blank=True, verbose_name='Not',
        help_text='Örn: Bu hafta A fabrikasına çekiliyor'
    )

    class Meta:
        verbose_name = 'POS Yönlendirme'
        verbose_name_plural = 'POS Yönlendirmeleri'

    def __str__(self):
        return f"{self.get_sale_mode_display()} → {self.pos_provider.name}"


class PaymentTransaction(models.Model):
    """Ödeme işlem kaydı."""

    STATUS_CHOICES = [
        ('pending', 'Beklemede'),
        ('success', 'Başarılı'),
        ('failed', 'Başarısız'),
        ('refunded', 'İade Edildi'),
    ]

    order = models.ForeignKey(
        'orders.Order', on_delete=models.CASCADE,
        related_name='transactions', verbose_name='Sipariş'
    )
    pos_provider = models.ForeignKey(
        POSProvider, on_delete=models.SET_NULL,
        null=True, verbose_name='POS Sağlayıcı'
    )
    amount = models.DecimalField(
        max_digits=12, decimal_places=2,
        verbose_name='Tutar (TL)'
    )
    installments = models.PositiveIntegerField(
        default=1, verbose_name='Taksit Sayısı'
    )
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES,
        default='pending', verbose_name='Durum'
    )
    transaction_id = models.CharField(
        max_length=200, blank=True,
        verbose_name='İşlem ID'
    )
    response_data = models.JSONField(
        default=dict, blank=True,
        verbose_name='POS Yanıt Verisi'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Ödeme İşlemi'
        verbose_name_plural = 'Ödeme İşlemleri'
        ordering = ['-created_at']

    def __str__(self):
        return f"Ödeme #{self.transaction_id} — {self.amount} TL"
