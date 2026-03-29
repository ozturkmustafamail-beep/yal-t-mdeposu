"""
Seed script — Yalitimdeposu.com
81 il, büyük illerin ilçeleri, örnek kategoriler, markalar, ürünler,
nakliye tarifeleri ve varsayılan POS sağlayıcı.
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'yalitimdeposu.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from decimal import Decimal
from apps.logistics.models import City, District, ShippingTariff, AmbarConfig
from apps.products.models import Category, Brand, Product
from apps.payments.models import POSProvider, POSRouting


def seed_cities():
    """81 il oluştur."""
    cities_data = [
        ('01', 'Adana', 'Akdeniz'), ('02', 'Adıyaman', 'Güneydoğu Anadolu'),
        ('03', 'Afyonkarahisar', 'Ege'), ('04', 'Ağrı', 'Doğu Anadolu'),
        ('05', 'Amasya', 'Karadeniz'), ('06', 'Ankara', 'İç Anadolu'),
        ('07', 'Antalya', 'Akdeniz'), ('08', 'Artvin', 'Karadeniz'),
        ('09', 'Aydın', 'Ege'), ('10', 'Balıkesir', 'Marmara'),
        ('11', 'Bilecik', 'Marmara'), ('12', 'Bingöl', 'Doğu Anadolu'),
        ('13', 'Bitlis', 'Doğu Anadolu'), ('14', 'Bolu', 'Karadeniz'),
        ('15', 'Burdur', 'Akdeniz'), ('16', 'Bursa', 'Marmara'),
        ('17', 'Çanakkale', 'Marmara'), ('18', 'Çankırı', 'İç Anadolu'),
        ('19', 'Çorum', 'Karadeniz'), ('20', 'Denizli', 'Ege'),
        ('21', 'Diyarbakır', 'Güneydoğu Anadolu'), ('22', 'Edirne', 'Marmara'),
        ('23', 'Elazığ', 'Doğu Anadolu'), ('24', 'Erzincan', 'Doğu Anadolu'),
        ('25', 'Erzurum', 'Doğu Anadolu'), ('26', 'Eskişehir', 'İç Anadolu'),
        ('27', 'Gaziantep', 'Güneydoğu Anadolu'), ('28', 'Giresun', 'Karadeniz'),
        ('29', 'Gümüşhane', 'Karadeniz'), ('30', 'Hakkari', 'Doğu Anadolu'),
        ('31', 'Hatay', 'Akdeniz'), ('32', 'Isparta', 'Akdeniz'),
        ('33', 'Mersin', 'Akdeniz'), ('34', 'İstanbul', 'Marmara'),
        ('35', 'İzmir', 'Ege'), ('36', 'Kars', 'Doğu Anadolu'),
        ('37', 'Kastamonu', 'Karadeniz'), ('38', 'Kayseri', 'İç Anadolu'),
        ('39', 'Kırklareli', 'Marmara'), ('40', 'Kırşehir', 'İç Anadolu'),
        ('41', 'Kocaeli', 'Marmara'), ('42', 'Konya', 'İç Anadolu'),
        ('43', 'Kütahya', 'Ege'), ('44', 'Malatya', 'Doğu Anadolu'),
        ('45', 'Manisa', 'Ege'), ('46', 'Kahramanmaraş', 'Akdeniz'),
        ('47', 'Mardin', 'Güneydoğu Anadolu'), ('48', 'Muğla', 'Ege'),
        ('49', 'Muş', 'Doğu Anadolu'), ('50', 'Nevşehir', 'İç Anadolu'),
        ('51', 'Niğde', 'İç Anadolu'), ('52', 'Ordu', 'Karadeniz'),
        ('53', 'Rize', 'Karadeniz'), ('54', 'Sakarya', 'Marmara'),
        ('55', 'Samsun', 'Karadeniz'), ('56', 'Siirt', 'Güneydoğu Anadolu'),
        ('57', 'Sinop', 'Karadeniz'), ('58', 'Sivas', 'İç Anadolu'),
        ('59', 'Tekirdağ', 'Marmara'), ('60', 'Tokat', 'Karadeniz'),
        ('61', 'Trabzon', 'Karadeniz'), ('62', 'Tunceli', 'Doğu Anadolu'),
        ('63', 'Şanlıurfa', 'Güneydoğu Anadolu'), ('64', 'Uşak', 'Ege'),
        ('65', 'Van', 'Doğu Anadolu'), ('66', 'Yozgat', 'İç Anadolu'),
        ('67', 'Zonguldak', 'Karadeniz'), ('68', 'Aksaray', 'İç Anadolu'),
        ('69', 'Bayburt', 'Karadeniz'), ('70', 'Karaman', 'İç Anadolu'),
        ('71', 'Kırıkkale', 'İç Anadolu'), ('72', 'Batman', 'Güneydoğu Anadolu'),
        ('73', 'Şırnak', 'Güneydoğu Anadolu'), ('74', 'Bartın', 'Karadeniz'),
        ('75', 'Ardahan', 'Doğu Anadolu'), ('76', 'Iğdır', 'Doğu Anadolu'),
        ('77', 'Yalova', 'Marmara'), ('78', 'Karabük', 'Karadeniz'),
        ('79', 'Kilis', 'Güneydoğu Anadolu'), ('80', 'Osmaniye', 'Akdeniz'),
        ('81', 'Düzce', 'Karadeniz'),
    ]

    created = 0
    for plate, name, region in cities_data:
        _, was_created = City.objects.get_or_create(
            plate_code=plate,
            defaults={'name': name, 'region': region}
        )
        if was_created:
            created += 1
    print(f"✅ {created} il oluşturuldu (toplam {City.objects.count()})")


def seed_districts():
    """Büyük illerin ilçelerini oluştur."""
    districts_data = {
        'İstanbul': [
            'Adalar', 'Arnavutköy', 'Ataşehir', 'Avcılar', 'Bağcılar', 'Bahçelievler',
            'Bakırköy', 'Başakşehir', 'Bayrampaşa', 'Beşiktaş', 'Beykoz', 'Beylikdüzü',
            'Beyoğlu', 'Büyükçekmece', 'Çatalca', 'Çekmeköy', 'Esenler', 'Esenyurt',
            'Eyüpsultan', 'Fatih', 'Gaziosmanpaşa', 'Güngören', 'Kadıköy', 'Kağıthane',
            'Kartal', 'Küçükçekmece', 'Maltepe', 'Pendik', 'Sancaktepe', 'Sarıyer',
            'Şile', 'Silivri', 'Sultanbeyli', 'Sultangazi', 'Şişli', 'Tuzla', 'Ümraniye',
            'Üsküdar', 'Zeytinburnu',
        ],
        'Ankara': [
            'Altındağ', 'Akyurt', 'Ayaş', 'Balâ', 'Beypazarı', 'Çamlıdere', 'Çankaya',
            'Çubuk', 'Elmadağ', 'Etimesgut', 'Evren', 'Gölbaşı', 'Güdül', 'Haymana',
            'Kalecik', 'Kazan', 'Keçiören', 'Kızılcahamam', 'Mamak', 'Nallıhan',
            'Polatlı', 'Pursaklar', 'Sincan', 'Şereflikoçhisar', 'Yenimahalle',
        ],
        'İzmir': [
            'Aliağa', 'Balçova', 'Bayındır', 'Bayraklı', 'Bergama', 'Beydağ', 'Bornova',
            'Buca', 'Çeşme', 'Çiğli', 'Dikili', 'Foça', 'Gaziemir', 'Güzelbahçe',
            'Karabağlar', 'Karşıyaka', 'Kemalpaşa', 'Kınık', 'Kiraz', 'Konak',
            'Menderes', 'Menemen', 'Narlıdere', 'Ödemiş', 'Seferihisar', 'Selçuk',
            'Tire', 'Torbalı', 'Urla',
        ],
        'Bursa': [
            'Gemlik', 'Gürsu', 'Harmancık', 'İnegöl', 'İznik', 'Karacabey', 'Keles',
            'Kestel', 'Mudanya', 'Mustafakemalpaşa', 'Nilüfer', 'Orhaneli', 'Orhangazi',
            'Osmangazi', 'Yenişehir', 'Yıldırım',
        ],
        'Antalya': [
            'Akseki', 'Aksu', 'Alanya', 'Demre', 'Döşemealtı', 'Elmalı', 'Finike',
            'Gazipaşa', 'Gündoğmuş', 'Kaş', 'Kemer', 'Kepez', 'Konyaaltı', 'Kumluca',
            'Manavgat', 'Muratpaşa', 'Serik',
        ],
        'Kocaeli': [
            'Başiskele', 'Çayırova', 'Darıca', 'Derince', 'Dilovası', 'Gebze',
            'Gölcük', 'İzmit', 'Kandıra', 'Karamürsel', 'Kartepe', 'Körfez',
        ],
    }

    created = 0
    for city_name, districts in districts_data.items():
        try:
            city = City.objects.get(name=city_name)
            for d_name in districts:
                _, was_created = District.objects.get_or_create(
                    city=city, name=d_name
                )
                if was_created:
                    created += 1
        except City.DoesNotExist:
            print(f"⚠️ {city_name} bulunamadı")
    print(f"✅ {created} ilçe oluşturuldu")


def seed_categories():
    """Ürün kategorileri."""
    categories = [
        ('Çatı Yalıtımı', 'cati-yalitimi', '🏠'),
        ('Dış Cephe Yalıtımı', 'dis-cephe-yalitimi', '🏗️'),
        ('Zemin Yalıtımı', 'zemin-yalitimi', '🏢'),
        ('Isı Yalıtımı', 'isi-yalitimi', '🌡️'),
        ('Su Yalıtımı', 'su-yalitimi', '💧'),
        ('Ses Yalıtımı', 'ses-yalitimi', '🔇'),
        ('Boya ve Sıva', 'boya-siva', '🎨'),
        ('Yapıştırıcı ve Bant', 'yapistirici-bant', '📎'),
    ]
    created = 0
    for i, (name, slug, icon) in enumerate(categories):
        _, was_created = Category.objects.get_or_create(
            slug=slug, defaults={'name': name, 'icon': icon, 'order': i}
        )
        if was_created:
            created += 1
    print(f"✅ {created} kategori oluşturuldu")


def seed_brands():
    """Markalar."""
    brands = [
        ('Köster', 'koster'), ('Aygips', 'aygips'), ('Hekim Yapı', 'hekim-yapi'),
        ('İzocam', 'izocam'), ('Betek', 'betek'), ('Teknoyalıtım', 'teknoyalitim'),
        ('Marshall', 'marshall'), ('Polisan', 'polisan'),
    ]
    created = 0
    for name, slug in brands:
        _, was_created = Brand.objects.get_or_create(
            slug=slug, defaults={'name': name}
        )
        if was_created:
            created += 1
    print(f"✅ {created} marka oluşturuldu")


def seed_products():
    """Örnek ürünler — çoklu fiyat kademeleri ile."""
    products = [
        {
            'name': 'Köster KBE Liquid Film',
            'slug': 'koster-kbe-liquid-film',
            'category': 'su-yalitimi', 'brand': 'koster', 'unit': 'Kova',
            'price_adet': Decimal('3000.00'),  # KDV + nakliye dahil
            'price_palet': Decimal('2100.00'),  # KDV hariç
            'price_tir': Decimal('1800.00'),    # KDV hariç
            'profit_margin_adet': Decimal('25'),
            'profit_margin_palet': Decimal('8'),
            'profit_margin_tir': Decimal('5'),
            'palet_quantity': 30, 'tir_quantity': 720, 'min_order_adet': 5,
            'weight_kg': Decimal('25'), 'width_cm': Decimal('35'), 'height_cm': Decimal('35'), 'depth_cm': Decimal('40'),
            'stock': 500, 'is_featured': True,
            'description': 'Tek komponentli, çözücüsüz, elastik su yalıtım malzemesi. Bodrum, teras ve balkon su yalıtımında kullanılır.',
            'specifications': 'Renk: Siyah\nUygulama: Fırça/Rulo\nKaplama: 1.5-2 kg/m²\nSertleşme: 24 saat\nSıcaklık Aralığı: -20°C ile +80°C',
        },
        {
            'name': 'Köster 21 Bitüm Membran',
            'slug': 'koster-21-bitum-membran',
            'category': 'su-yalitimi', 'brand': 'koster', 'unit': 'Rulo',
            'price_adet': Decimal('2160.00'),
            'price_palet': Decimal('1500.00'),
            'price_tir': Decimal('1250.00'),
            'profit_margin_adet': Decimal('20'),
            'profit_margin_palet': Decimal('10'),
            'profit_margin_tir': Decimal('5'),
            'palet_quantity': 20, 'tir_quantity': 480, 'min_order_adet': 5,
            'weight_kg': Decimal('30'), 'width_cm': Decimal('100'), 'height_cm': Decimal('25'), 'depth_cm': Decimal('25'),
            'stock': 300, 'is_featured': True,
            'description': 'Yüksek performanslı bitümlü su yalıtım membranı.',
        },
        {
            'name': 'İzocam Taş Yünü Panel 5cm',
            'slug': 'izocam-tas-yunu-5cm',
            'category': 'isi-yalitimi', 'brand': 'izocam', 'unit': 'Paket',
            'price_adet': Decimal('420.00'),
            'price_palet': Decimal('290.00'),
            'price_tir': Decimal('240.00'),
            'profit_margin_adet': Decimal('22'),
            'profit_margin_palet': Decimal('8'),
            'profit_margin_tir': Decimal('4'),
            'palet_quantity': 40, 'tir_quantity': 800, 'min_order_adet': 5,
            'weight_kg': Decimal('15'), 'width_cm': Decimal('60'), 'height_cm': Decimal('120'), 'depth_cm': Decimal('5'),
            'stock': 800, 'is_factory_direct': True, 'is_featured': True,
            'description': 'Yüksek yoğunluklu taş yünü yalıtım paneli. A1 sınıfı yanmaz.',
        },
        {
            'name': 'Hekim EPS Strafor Levha 3cm',
            'slug': 'hekim-eps-strafor-3cm',
            'category': 'isi-yalitimi', 'brand': 'hekim-yapi', 'unit': 'Adet',
            'price_adet': Decimal('54.00'),
            'price_palet': Decimal('38.00'),
            'price_tir': Decimal('30.00'),
            'profit_margin_adet': Decimal('20'),
            'profit_margin_palet': Decimal('10'),
            'profit_margin_tir': Decimal('5'),
            'palet_quantity': 100, 'tir_quantity': 2000, 'min_order_adet': 10,
            'weight_kg': Decimal('0.50'), 'width_cm': Decimal('50'), 'height_cm': Decimal('100'), 'depth_cm': Decimal('3'),
            'stock': 5000, 'is_factory_direct': True, 'is_featured': True,
            'description': 'Genleştirilmiş polistiren (EPS) ısı yalıtım levhası.',
        },
        {
            'name': 'Köster Deuxan 2C Çimento Esaslı',
            'slug': 'koster-deuxan-2c',
            'category': 'su-yalitimi', 'brand': 'koster', 'unit': 'Set',
            'price_adet': Decimal('3840.00'),
            'price_palet': Decimal('2800.00'),
            'price_tir': Decimal('2400.00'),
            'profit_margin_adet': Decimal('18'),
            'profit_margin_palet': Decimal('7'),
            'profit_margin_tir': Decimal('4'),
            'palet_quantity': 20, 'tir_quantity': 360, 'min_order_adet': 5,
            'weight_kg': Decimal('32'), 'width_cm': Decimal('40'), 'height_cm': Decimal('40'), 'depth_cm': Decimal('45'),
            'stock': 200, 'is_featured': True,
            'description': 'İki komponentli, çimento esaslı elastik su yalıtım malzemesi.',
        },
        {
            'name': 'Teknoyalıtım XPS Levha 4cm',
            'slug': 'tekno-xps-4cm',
            'category': 'zemin-yalitimi', 'brand': 'teknoyalitim', 'unit': 'Adet',
            'price_adet': Decimal('102.00'),
            'price_palet': Decimal('70.00'),
            'price_tir': Decimal('55.00'),
            'profit_margin_adet': Decimal('22'),
            'profit_margin_palet': Decimal('12'),
            'profit_margin_tir': Decimal('6'),
            'palet_quantity': 60, 'tir_quantity': 1200, 'min_order_adet': 5,
            'weight_kg': Decimal('1.20'), 'width_cm': Decimal('60'), 'height_cm': Decimal('120'), 'depth_cm': Decimal('4'),
            'stock': 3000, 'is_factory_direct': True, 'is_featured': True,
            'description': 'Ekstrüde polistiren (XPS) zemin yalıtım levhası.',
        },
        {
            'name': 'Betek Elastik Dış Cephe Boyası',
            'slug': 'betek-elastik-boya',
            'category': 'boya-siva', 'brand': 'betek', 'unit': 'Kova',
            'price_adet': Decimal('1440.00'),
            'price_palet': Decimal('1000.00'),
            'price_tir': None,  # Tır yok
            'profit_margin_adet': Decimal('20'),
            'profit_margin_palet': Decimal('8'),
            'palet_quantity': 24, 'tir_quantity': 0, 'min_order_adet': 5,
            'weight_kg': Decimal('20'), 'width_cm': Decimal('30'), 'height_cm': Decimal('30'), 'depth_cm': Decimal('35'),
            'stock': 400, 'is_featured': True,
            'description': 'Elastik su bazlı dış cephe boyası, çatlak köprüleme özellikli.',
        },
        {
            'name': 'İzocam Cam Yünü Şilte 10cm',
            'slug': 'izocam-cam-yunu-10cm',
            'category': 'ses-yalitimi', 'brand': 'izocam', 'unit': 'Rulo',
            'price_adet': Decimal('336.00'),
            'price_palet': Decimal('230.00'),
            'price_tir': Decimal('190.00'),
            'profit_margin_adet': Decimal('20'),
            'profit_margin_palet': Decimal('10'),
            'profit_margin_tir': Decimal('5'),
            'palet_quantity': 30, 'tir_quantity': 600, 'min_order_adet': 5,
            'weight_kg': Decimal('12'), 'width_cm': Decimal('120'), 'height_cm': Decimal('12'), 'depth_cm': Decimal('35'),
            'stock': 600, 'is_factory_direct': True, 'is_featured': True,
            'description': 'Cam yünü ses ve ısı yalıtım şiltesi.',
        },
        {
            'name': 'Köster TPO Membran 1.5mm',
            'slug': 'koster-tpo-membran',
            'category': 'cati-yalitimi', 'brand': 'koster', 'unit': 'Rulo',
            'price_adet': Decimal('5400.00'),
            'price_palet': Decimal('3800.00'),
            'price_tir': Decimal('3200.00'),
            'profit_margin_adet': Decimal('20'),
            'profit_margin_palet': Decimal('8'),
            'profit_margin_tir': Decimal('4'),
            'palet_quantity': 15, 'tir_quantity': 300, 'min_order_adet': 3,
            'weight_kg': Decimal('35'), 'width_cm': Decimal('200'), 'height_cm': Decimal('30'), 'depth_cm': Decimal('30'),
            'stock': 150,
            'description': 'TPO bazlı çatı su yalıtım membranı.',
        },
        {
            'name': 'Aygips Alçıpan Levha 12.5mm',
            'slug': 'aygips-alcipan-12-5mm',
            'category': 'dis-cephe-yalitimi', 'brand': 'aygips', 'unit': 'Adet',
            'price_adet': Decimal('216.00'),
            'price_palet': Decimal('150.00'),
            'price_tir': Decimal('120.00'),
            'profit_margin_adet': Decimal('20'),
            'profit_margin_palet': Decimal('10'),
            'profit_margin_tir': Decimal('5'),
            'palet_quantity': 50, 'tir_quantity': 1000, 'min_order_adet': 5,
            'weight_kg': Decimal('27'), 'width_cm': Decimal('120'), 'height_cm': Decimal('250'), 'depth_cm': Decimal('1.25'),
            'stock': 2000, 'is_factory_direct': True,
            'description': 'Standart alçıpan levha, iç mekan bölme duvar ve asma tavan uygulamaları.',
        },
    ]

    created = 0
    for p_data in products:
        cat = Category.objects.get(slug=p_data.pop('category'))
        brand = Brand.objects.get(slug=p_data.pop('brand'))
        _, was_created = Product.objects.get_or_create(
            slug=p_data['slug'],
            defaults={**p_data, 'category': cat, 'brand': brand}
        )
        if was_created:
            created += 1
    print(f"✅ {created} ürün oluşturuldu")


def seed_shipping():
    """Bölge bazlı nakliye tarifeleri."""
    import random

    region_rates = {
        'Marmara': 3,
        'Ege': 5,
        'Akdeniz': 6,
        'İç Anadolu': 8,
        'Karadeniz': 10,
        'Doğu Anadolu': 14,
        'Güneydoğu Anadolu': 12,
    }

    # Genel tarife (bölge bazlı)
    created = 0
    for region, rate in region_rates.items():
        _, was_created = ShippingTariff.objects.get_or_create(
            provider_name='Horoz Lojistik',
            region=region,
            city=None,
            defaults={
                'calc_type': 'per_kg',
                'cost': Decimal(str(rate)),
                'min_charge': Decimal('50.00'),
            }
        )
        if was_created:
            created += 1

    # Ambar config (bölge bazlı)
    for region, rate in region_rates.items():
        AmbarConfig.objects.get_or_create(
            region=region,
            city=None,
            defaults={
                'estimated_fee_per_kg': Decimal(str(rate * 0.5)),
            }
        )

    print(f"✅ {created} nakliye tarifesi oluşturuldu")


def seed_pos():
    """POS sağlayıcılar."""
    # Şirket POS (adet siparişleri)
    company_pos, _ = POSProvider.objects.get_or_create(
        name='Yalıtım Deposu POS',
        defaults={
            'provider_type': 'company',
            'is_active': True,
            'max_installments': 12,
            'installment_rates': {'2': 0, '3': 0, '6': 1.5, '9': 3.0, '12': 5.0},
        }
    )

    # Fabrika POS'ları
    factory_a, _ = POSProvider.objects.get_or_create(
        name='Köster Fabrika POS',
        defaults={
            'provider_type': 'factory',
            'factory_name': 'Köster Kimya',
            'is_active': True,
            'max_installments': 1,
        }
    )
    factory_b, _ = POSProvider.objects.get_or_create(
        name='İzocam Fabrika POS',
        defaults={
            'provider_type': 'factory',
            'factory_name': 'İzocam A.Ş.',
            'is_active': True,
            'max_installments': 1,
        }
    )

    # POS Routing
    POSRouting.objects.get_or_create(
        sale_mode='ADET',
        defaults={'pos_provider': company_pos, 'is_active': True}
    )
    POSRouting.objects.get_or_create(
        sale_mode='TOPTAN',
        defaults={'pos_provider': factory_a, 'is_active': True, 'notes': 'Köster fabrikasına çekiliyor'}
    )

    print("✅ POS sağlayıcılar ve yönlendirmeler oluşturuldu")


if __name__ == '__main__':
    print("🚀 Yalıtım Deposu Seed Data Yükleniyor...\n")
    seed_cities()
    seed_districts()
    seed_categories()
    seed_brands()
    seed_products()
    seed_shipping()
    seed_pos()
    print("\n✅ Tüm seed veriler yüklendi!")
