from django.db import models


class Category(models.Model):
    """Ürün kategorisi (Çatı Yalıtımı, Su Yalıtımı vb.)."""
    name = models.CharField(max_length=100, verbose_name='Kategori Adı')
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True, verbose_name='Açıklama')
    icon = models.CharField(max_length=50, blank=True, verbose_name='İkon (emoji veya CSS class)')
    image = models.ImageField(
        upload_to='categories/', blank=True, null=True,
        verbose_name='Kategori Görseli'
    )
    order = models.PositiveIntegerField(default=0, verbose_name='Sıralama')
    is_active = models.BooleanField(default=True, verbose_name='Aktif')

    class Meta:
        verbose_name = 'Kategori'
        verbose_name_plural = 'Kategoriler'
        ordering = ['order', 'name']

    def __str__(self):
        return self.name


class Brand(models.Model):
    """Ürün markası."""
    name = models.CharField(max_length=100, verbose_name='Marka Adı')
    slug = models.SlugField(unique=True)
    logo = models.ImageField(upload_to='brands/', blank=True, null=True, verbose_name='Logo')
    is_active = models.BooleanField(default=True, verbose_name='Aktif')

    class Meta:
        verbose_name = 'Marka'
        verbose_name_plural = 'Markalar'
        ordering = ['name']

    def __str__(self):
        return self.name


class Product(models.Model):
    """
    Ürün modeli — çoklu fiyat kademesi.

    Fiyat Kuralları:
    ┌──────────┬───────────────────────────────┐
    │ ADET     │ KDV dahil, nakliye dahil      │
    │ PALET    │ KDV hariç, nakliye hariç      │
    │ TIR      │ KDV hariç, nakliye hariç      │
    └──────────┴───────────────────────────────┘
    """
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE,
        related_name='products', verbose_name='Kategori'
    )
    brand = models.ForeignKey(
        Brand, on_delete=models.CASCADE,
        related_name='products', verbose_name='Marka'
    )
    name = models.CharField(max_length=300, verbose_name='Ürün Adı')
    slug = models.SlugField(unique=True, max_length=350)
    description = models.TextField(blank=True, verbose_name='Ürün Açıklaması')
    specifications = models.TextField(
        blank=True, verbose_name='Teknik Özellikler',
        help_text='Her satır bir özellik. Örn: Renk: Beyaz'
    )
    image = models.ImageField(
        upload_to='products/', blank=True, null=True,
        verbose_name='Ürün Görseli'
    )
    unit = models.CharField(
        max_length=50, default='Adet',
        verbose_name='Birim (Adet, Kova, Rulo, Paket vb.)'
    )

    # Ağırlık & Ebat — nakliye hesabı için
    weight_kg = models.DecimalField(
        max_digits=8, decimal_places=2, default=0,
        verbose_name='Ağırlık (kg)',
        help_text='Birim başına ağırlık — ambar ücreti hesabında kullanılır'
    )
    width_cm = models.DecimalField(
        max_digits=6, decimal_places=1, default=0,
        verbose_name='Genişlik (cm)'
    )
    height_cm = models.DecimalField(
        max_digits=6, decimal_places=1, default=0,
        verbose_name='Yükseklik (cm)'
    )
    depth_cm = models.DecimalField(
        max_digits=6, decimal_places=1, default=0,
        verbose_name='Derinlik (cm)'
    )

    # ─── Fiyatlar ────────────────────────────────────────
    # ADET: KDV dahil, nakliye dahil nihai fiyat
    price_adet = models.DecimalField(
        max_digits=10, decimal_places=2,
        verbose_name='Adet Fiyatı (KDV dahil, nakliye dahil)',
        help_text='Tüketiciye gösterilecek nihai birim fiyat'
    )
    # PALET: KDV hariç fab. çıkış birim fiyat (nullable — yoksa palet satılmaz)
    price_palet = models.DecimalField(
        max_digits=10, decimal_places=2,
        null=True, blank=True,
        verbose_name='Palet Birim Fiyatı (KDV hariç)',
        help_text='Boş bırakılırsa ürün palet olarak satılmaz'
    )
    # TIR: KDV hariç fab. çıkış birim fiyat (nullable)
    price_tir = models.DecimalField(
        max_digits=10, decimal_places=2,
        null=True, blank=True,
        verbose_name='Tır Birim Fiyatı (KDV hariç)',
        help_text='Boş bırakılırsa ürün tır olarak satılmaz'
    )

    # Kâr Marjı bilgisi (admin için, müşteriye gösterilmez)
    profit_margin_adet = models.DecimalField(
        max_digits=5, decimal_places=2, default=0,
        verbose_name='Adet Kâr Marjı (%)',
        help_text='Sadece admin referansı'
    )
    profit_margin_palet = models.DecimalField(
        max_digits=5, decimal_places=2, default=0,
        verbose_name='Palet Kâr Marjı (%)',
        help_text='Sadece admin referansı'
    )
    profit_margin_tir = models.DecimalField(
        max_digits=5, decimal_places=2, default=0,
        verbose_name='Tır Kâr Marjı (%)',
        help_text='Sadece admin referansı'
    )

    # KDV oranı
    kdv_rate = models.PositiveIntegerField(
        default=20, verbose_name='KDV Oranı (%)'
    )

    # ─── Sipariş Limitleri ───────────────────────────────
    min_order_adet = models.PositiveIntegerField(
        default=1, verbose_name='Minimum Adet Sipariş'
    )
    palet_quantity = models.PositiveIntegerField(
        default=0, verbose_name='Bir Paletteki Adet Sayısı',
        help_text='0 ise palet satışı yok'
    )
    tir_quantity = models.PositiveIntegerField(
        default=0, verbose_name='Bir Tırdaki Adet Sayısı',
        help_text='0 ise tır satışı yok'
    )

    # ─── Stok & Durum ───────────────────────────────────
    stock = models.PositiveIntegerField(default=0, verbose_name='Depo Stoğu')
    is_factory_direct = models.BooleanField(
        default=False,
        verbose_name='Fabrikadan Direkt Sevk'
    )
    is_active = models.BooleanField(default=True, verbose_name='Aktif')
    is_featured = models.BooleanField(default=False, verbose_name='Öne Çıkan')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Ürün'
        verbose_name_plural = 'Ürünler'
        ordering = ['category', 'name']

    def __str__(self):
        return f"{self.brand.name} — {self.name}"

    @property
    def has_palet(self):
        return self.price_palet is not None and self.palet_quantity > 0

    @property
    def has_tir(self):
        return self.price_tir is not None and self.tir_quantity > 0

    @property
    def available_modes(self):
        """Ürün için mevcut satış modları."""
        modes = ['ADET']
        if self.has_palet:
            modes.append('PALET')
        if self.has_tir:
            modes.append('TIR')
        return modes

    @property
    def volumetric_weight(self):
        """Hacimsel ağırlık (desi) hesabı — lojistik için."""
        if self.width_cm and self.height_cm and self.depth_cm:
            return (self.width_cm * self.height_cm * self.depth_cm) / 3000
        return self.weight_kg

    @property
    def chargeable_weight(self):
        """Ücretlendirilebilir ağırlık — gerçek ve hacimsel ağırlığın büyüğü."""
        from decimal import Decimal
        vol = self.volumetric_weight or Decimal('0')
        real = self.weight_kg or Decimal('0')
        return max(vol, real)
