from django.db import models


class City(models.Model):
    """Türkiye'nin 81 ili."""
    name = models.CharField(max_length=50, verbose_name='İl Adı')
    plate_code = models.CharField(max_length=2, unique=True, verbose_name='Plaka Kodu')
    region = models.CharField(max_length=50, blank=True, verbose_name='Bölge')

    class Meta:
        verbose_name = 'İl'
        verbose_name_plural = 'İller'
        ordering = ['name']

    def __str__(self):
        return f"{self.plate_code} — {self.name}"


class District(models.Model):
    """İlçe."""
    city = models.ForeignKey(
        City, on_delete=models.CASCADE,
        related_name='districts', verbose_name='İl'
    )
    name = models.CharField(max_length=100, verbose_name='İlçe Adı')

    class Meta:
        verbose_name = 'İlçe'
        verbose_name_plural = 'İlçeler'
        ordering = ['name']
        unique_together = ['city', 'name']

    def __str__(self):
        return f"{self.name} / {self.city.name}"


class ShippingTariff(models.Model):
    """
    Nakliye tarifeleri — lojistik şirketinden gelen veriler.
    Admin panelden veya gelecekte API ile güncellenecek.
    """
    CALC_TYPE_CHOICES = [
        ('per_kg', 'Kilogram Başına'),
        ('per_desi', 'Desi Başına'),
        ('per_unit', 'Birim Başına (sabit)'),
    ]

    provider_name = models.CharField(
        max_length=100, verbose_name='Lojistik Firma',
        help_text='Örn: Aras Kargo, Horoz Lojistik'
    )
    # Bölge veya şehir bazlı ücretlendirme
    region = models.CharField(
        max_length=50, blank=True, verbose_name='Bölge',
        help_text='Boş bırakılırsa tüm bölgelere uygulanır'
    )
    city = models.ForeignKey(
        City, on_delete=models.CASCADE,
        null=True, blank=True,
        related_name='shipping_tariffs', verbose_name='İl',
        help_text='Şehir bazlı tarife (öncelikli)'
    )
    calc_type = models.CharField(
        max_length=20, choices=CALC_TYPE_CHOICES,
        default='per_kg', verbose_name='Hesaplama Tipi'
    )
    cost = models.DecimalField(
        max_digits=10, decimal_places=2,
        verbose_name='Birim Maliyet (TL)',
        help_text='kg başına, desi başına veya sabit — tipe göre'
    )
    min_charge = models.DecimalField(
        max_digits=10, decimal_places=2, default=0,
        verbose_name='Minimum Ücret (TL)',
        help_text='Hesaplanan tutar bunun altındaysa bu tutar uygulanır'
    )
    is_active = models.BooleanField(default=True, verbose_name='Aktif')
    notes = models.TextField(blank=True, verbose_name='Notlar')

    class Meta:
        verbose_name = 'Nakliye Tarifesi'
        verbose_name_plural = 'Nakliye Tarifeleri'
        ordering = ['provider_name', 'region']

    def __str__(self):
        target = self.city.name if self.city else (self.region or 'Genel')
        return f"{self.provider_name} → {target}: {self.cost} TL/{self.get_calc_type_display()}"


class AmbarConfig(models.Model):
    """
    Ambar ücreti konfigürasyonu.
    Lojistik şirketlerinin ambar depolama ücretleri.
    """
    city = models.ForeignKey(
        City, on_delete=models.CASCADE,
        null=True, blank=True,
        related_name='ambar_configs', verbose_name='İl'
    )
    region = models.CharField(
        max_length=50, blank=True, verbose_name='Bölge'
    )
    estimated_fee_per_kg = models.DecimalField(
        max_digits=10, decimal_places=2, default=0,
        verbose_name='Tahmini kg Başı Ambar Ücreti (TL)'
    )
    notes = models.TextField(
        blank=True,
        default='Kesin ücret sevkiyat günü belirlenir.',
        verbose_name='Not'
    )

    class Meta:
        verbose_name = 'Ambar Ayarı'
        verbose_name_plural = 'Ambar Ayarları'

    def __str__(self):
        target = self.city.name if self.city else (self.region or 'Genel')
        return f"Ambar: {target} — {self.estimated_fee_per_kg} TL/kg"
