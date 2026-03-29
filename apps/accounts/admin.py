from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Address


class AddressInline(admin.TabularInline):
    model = Address
    extra = 0


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'company_name', 'phone', 'is_plus_display', 'plus_until', 'total_spent']
    list_filter = ['is_active', 'is_staff']
    search_fields = ['username', 'email', 'company_name', 'phone']
    inlines = [AddressInline]

    fieldsets = UserAdmin.fieldsets + (
        ('İş Bilgileri', {
            'fields': ('phone', 'company_name', 'tax_number'),
        }),
        ('Plus Hesap (Sadakat)', {
            'fields': ('total_spent', 'plus_until'),
        }),
    )

    @admin.display(description='Plus', boolean=True)
    def is_plus_display(self, obj):
        return obj.is_plus


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ['user', 'title', 'city', 'district', 'is_default']
    list_filter = ['city', 'is_default']
    search_fields = ['user__username', 'title', 'address_line']
