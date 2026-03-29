from django.contrib import admin
from .models import City, District, ShippingTariff, AmbarConfig


class DistrictInline(admin.TabularInline):
    model = District
    extra = 0


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ['plate_code', 'name', 'region', 'district_count']
    list_filter = ['region']
    search_fields = ['name', 'plate_code']
    inlines = [DistrictInline]

    @admin.display(description='İlçe Sayısı')
    def district_count(self, obj):
        return obj.districts.count()


@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):
    list_display = ['name', 'city']
    list_filter = ['city']
    search_fields = ['name', 'city__name']


@admin.register(ShippingTariff)
class ShippingTariffAdmin(admin.ModelAdmin):
    list_display = ['provider_name', 'city', 'region', 'calc_type', 'cost', 'min_charge', 'is_active']
    list_filter = ['provider_name', 'region', 'calc_type', 'is_active']
    list_editable = ['cost', 'min_charge', 'is_active']
    search_fields = ['provider_name', 'city__name', 'region']


@admin.register(AmbarConfig)
class AmbarConfigAdmin(admin.ModelAdmin):
    list_display = ['city', 'region', 'estimated_fee_per_kg', 'notes']
    list_filter = ['region']
    list_editable = ['estimated_fee_per_kg']
