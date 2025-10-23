from django.contrib import admin
from .models import Service, FishCategory, ArrivalNote

# Register your models here.


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'category', 'amount', 'status', 'created_at']
    list_filter = ['status', 'category', 'created_at']
    search_fields = ['code', 'name', 'description']
    readonly_fields = ['created_at', 'updated_at', 'created_by']

    fieldsets = (
        ('Identification', {
            'fields': ('code', 'name')
        }),
        ('Détails du service', {
            'fields': ('category', 'description', 'amount', 'status')
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at', 'created_by'),
            'classes': ('collapse',)
        }),
    )

    def save_model(self, request, obj, form, change):
        if not change:  # Si c'est une nouvelle instance
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(FishCategory)
class FishCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Informations', {
            'fields': ('name', 'description', 'is_active')
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(ArrivalNote)
class ArrivalNoteAdmin(admin.ModelAdmin):
    list_display = ['lot_id', 'client', 'reception_date', 'weight', 'fish_category', 'service_type', 'status', 'created_at']
    list_filter = ['status', 'service_type', 'reception_date', 'created_at', 'fish_category']
    search_fields = ['lot_id', 'client__name', 'client__accounting_code']
    readonly_fields = ['lot_id', 'created_at', 'updated_at', 'created_by']
    date_hierarchy = 'reception_date'

    fieldsets = (
        ('Identification', {
            'fields': ('lot_id', 'client', 'reception_date')
        }),
        ('Détails du lot', {
            'fields': ('weight', 'fish_category', 'service_type')
        }),
        ('Statut et observations', {
            'fields': ('status', 'observations', 'rejection_reason')
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at', 'created_by')
        }),
    )

    def save_model(self, request, obj, form, change):
        if not change:  # Si c'est une nouvelle instance
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
