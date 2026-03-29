from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from datetime import timedelta
from django.conf import settings


class CustomUser(AbstractUser):
    """
    Genişletilmiş kullanıcı modeli.
    - Nalbur/Usta hedef kitlesi
    - Plus hesap (sadakat programı)
    - Adres yönetimi (ayrı model)
    """
    phone = models.CharField(max_length=20, blank=True, verbose_name='Telefon')
    company_name = models.CharField(max_length=200, blank=True, verbose_name='Firma / İşyeri Adı')
    tax_number = models.CharField(max_length=20, blank=True, verbose_name='Vergi No')

    # Plus Hesap (Sadakat Programı)
    total_spent = models.DecimalField(
        max_digits=12, decimal_places=2, default=0,
        verbose_name='Toplam Harcama (TL)'
    )
    plus_until = models.DateTimeField(
        null=True, blank=True,
        verbose_name='Plus Hesap Bitiş Tarihi'
    )

    class Meta:
        verbose_name = 'Kullanıcı'
        verbose_name_plural = 'Kullanıcılar'

    @property
    def is_plus(self):
        """Plus hesap aktif mi kontrol et."""
        if self.plus_until and self.plus_until > timezone.now():
            return True
        return False

    @property
    def plus_days_remaining(self):
        """Plus hesap kaç gün kaldı."""
        if self.is_plus:
            delta = self.plus_until - timezone.now()
            return max(0, delta.days)
        return 0

    def activate_plus(self):
        """Plus hesabı aktive et veya süreyi yenile."""
        duration = getattr(settings, 'PLUS_DURATION_DAYS', 30)
        self.plus_until = timezone.now() + timedelta(days=duration)
        self.save(update_fields=['plus_until'])

    def add_spending(self, amount):
        """Harcama ekle, eşik aşılırsa Plus aktive et."""
        from decimal import Decimal
        threshold = Decimal(str(getattr(settings, 'PLUS_THRESHOLD', 10000)))
        self.total_spent += Decimal(str(amount))
        self.save(update_fields=['total_spent'])
        # Tek seferde eşik aşıldıysa Plus aktive et
        if Decimal(str(amount)) >= threshold:
            self.activate_plus()


class Address(models.Model):
    """Kullanıcı teslimat adresi."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='addresses', verbose_name='Kullanıcı'
    )
    title = models.CharField(
        max_length=100, verbose_name='Adres Başlığı',
        help_text='Örn: Dükkan, Ev, Şantiye'
    )
    city = models.ForeignKey(
        'logistics.City', on_delete=models.CASCADE,
        verbose_name='İl'
    )
    district = models.ForeignKey(
        'logistics.District', on_delete=models.CASCADE,
        verbose_name='İlçe'
    )
    address_line = models.TextField(verbose_name='Açık Adres')
    postal_code = models.CharField(max_length=10, blank=True, verbose_name='Posta Kodu')
    is_default = models.BooleanField(default=False, verbose_name='Varsayılan Adres')

    class Meta:
        verbose_name = 'Adres'
        verbose_name_plural = 'Adresler'

    def __str__(self):
        return f"{self.title} — {self.district.name}, {self.city.name}"

    def save(self, *args, **kwargs):
        # Yeni varsayılan ayarlanırsa eskisini kaldır
        if self.is_default:
            Address.objects.filter(user=self.user, is_default=True).update(is_default=False)
        super().save(*args, **kwargs)
