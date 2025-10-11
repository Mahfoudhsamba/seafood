from django.contrib import admin
from .models import Client

# Register your models here.

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ['accounting_code', 'name', 'client_type', 'status', 'city', 'created_at']
    list_filter = ['status', 'client_type', 'country', 'created_at']
    search_fields = ['accounting_code', 'name', 'email', 'mobile', 'phone', 'tax_id', 'trade_register']
    readonly_fields = ['accounting_code', 'created_at', 'updated_at']

    fieldsets = (
        ('Informations de base', {
            'fields': ('accounting_code', 'name', 'client_type', 'responsible', 'status')
        }),
        ('Coordonnées', {
            'fields': ('email', 'mobile', 'phone', 'website')
        }),
        ('Adresse', {
            'fields': ('address', 'city', 'postal_code', 'country')
        }),
        ('Informations légales', {
            'fields': ('trade_register', 'tax_id')
        }),
        ('Autres', {
            'fields': ('logo', 'observations', 'created_at', 'updated_at')
        }),
    )
