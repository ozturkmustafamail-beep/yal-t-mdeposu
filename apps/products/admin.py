from django.contrib import admin
from .models import Category, Brand, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'order', 'is_active']
    list_editable = ['order', 'is_active']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'is_active']
    list_editable = ['is_active']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'brand', 'category',
        'price_adet', 'price_palet', 'price_tir',
        'profit_margin_adet', 'profit_margin_palet', 'profit_margin_tir',
        'min_order_adet', 'stock', 'is_active', 'is_featured',
    ]
    list_filter = ['category', 'brand', 'is_active', 'is_featured', 'is_factory_direct']
    search_fields = ['name', 'brand__name', 'description']
    list_editable = ['price_adet', 'price_palet', 'price_tir', 'is_active', 'is_featured']
    prepopulated_fields = {'slug': ('name',)}

    fieldsets = (
        ('Temel Bilgiler', {
            'fields': (
                'category', 'brand', 'name', 'slug',
                'description', 'specifications', 'image', 'unit',
            ),
        }),
        ('Fiyatlar & Kâr Marjları', {
            'fields': (
                ('price_adet', 'profit_margin_adet'),
                ('price_palet', 'profit_margin_palet'),
                ('price_tir', 'profit_margin_tir'),
                'kdv_rate',
            ),
            'description': 'ADET: KDV dahil, nakliye dahil | PALET/TIR: KDV hariç, nakliye hariç',
        }),
        ('Ağırlık & Ebat (Nakliye Hesabı)', {
            'fields': ('weight_kg', 'width_cm', 'height_cm', 'depth_cm'),
            'classes': ('collapse',),
        }),
        ('Sipariş Limitleri', {
            'fields': ('min_order_adet', 'palet_quantity', 'tir_quantity'),
        }),
        ('Stok & Durum', {
            'fields': ('stock', 'is_factory_direct', 'is_active', 'is_featured'),
        }),
    )
