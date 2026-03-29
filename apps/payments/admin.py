from django.contrib import admin
from .models import POSProvider, POSRouting, PaymentTransaction


@admin.register(POSProvider)
class POSProviderAdmin(admin.ModelAdmin):
    list_display = ['name', 'provider_type', 'factory_name', 'is_active', 'max_installments']
    list_filter = ['provider_type', 'is_active']
    list_editable = ['is_active']


@admin.register(POSRouting)
class POSRoutingAdmin(admin.ModelAdmin):
    list_display = ['sale_mode', 'pos_provider', 'is_active', 'valid_from', 'valid_until', 'notes']
    list_filter = ['sale_mode', 'is_active']
    list_editable = ['is_active']


@admin.register(PaymentTransaction)
class PaymentTransactionAdmin(admin.ModelAdmin):
    list_display = ['transaction_id', 'order', 'pos_provider', 'amount', 'installments', 'status', 'created_at']
    list_filter = ['status', 'pos_provider', 'created_at']
    readonly_fields = ['transaction_id', 'response_data', 'created_at']
