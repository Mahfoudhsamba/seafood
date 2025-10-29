from django.contrib import admin
from .models import Service, FishCategory, ArrivalNote, Classification, ClassificationItem

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
    list_display = ['lot_id', 'client', 'reception_date', 'weight', 'get_service_category', 'service_type', 'status', 'created_at']
    list_filter = ['status', 'service_type', 'reception_date', 'created_at', 'service_type__category']
    search_fields = ['lot_id', 'client__name', 'client__accounting_code']
    readonly_fields = ['lot_id', 'created_at', 'updated_at', 'created_by']
    date_hierarchy = 'reception_date'

    fieldsets = (
        ('Identification', {
            'fields': ('lot_id', 'client', 'reception_date')
        }),
        ('Détails du lot', {
            'fields': ('weight', 'service_type')
        }),
        ('Statut et observations', {
            'fields': ('status', 'observations', 'rejection_reason')
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at', 'created_by')
        }),
    )

    def get_service_category(self, obj):
        """Retourne la catégorie du service"""
        return obj.service_type.category.name if obj.service_type and obj.service_type.category else '-'
    get_service_category.short_description = 'Catégorie'

    def save_model(self, request, obj, form, change):
        if not change:  # Si c'est une nouvelle instance
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


class ClassificationItemInline(admin.TabularInline):
    """
    Inline pour gérer les détails par espèce directement depuis le rapport
    """
    model = ClassificationItem
    extra = 1
    fields = ['species', 'custom_species_name', 'weight', 'comment']
    verbose_name = 'Détail par espèce'
    verbose_name_plural = 'Détails par espèce'


@admin.register(Classification)
class ClassificationAdmin(admin.ModelAdmin):
    list_display = ['arrival_note', 'classification_date', 'status', 'get_total_weight', 'created_by']
    list_filter = ['status', 'classification_date', 'created_at']
    search_fields = ['arrival_note__lot_id', 'arrival_note__client__name', 'general_observation']
    readonly_fields = ['classification_date', 'created_at', 'updated_at', 'created_by']
    date_hierarchy = 'classification_date'
    inlines = [ClassificationItemInline]

    fieldsets = (
        ('Informations principales', {
            'fields': ('arrival_note', 'classification_date', 'status')
        }),
        ('Observations', {
            'fields': ('general_observation',)
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at', 'created_by'),
            'classes': ('collapse',)
        }),
    )

    def get_total_weight(self, obj):
        """Retourne le poids total de tous les items"""
        return f"{obj.total_weight} kg"
    get_total_weight.short_description = 'Poids total'

    def save_model(self, request, obj, form, change):
        if not change:  # Si c'est une nouvelle instance
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        """Optimise les requêtes en préchargeant les relations"""
        qs = super().get_queryset(request)
        return qs.select_related('arrival_note', 'arrival_note__client', 'created_by').prefetch_related('items')


@admin.register(ClassificationItem)
class ClassificationItemAdmin(admin.ModelAdmin):
    list_display = ['classification', 'get_species_name', 'weight', 'created_at']
    list_filter = ['species', 'created_at']
    search_fields = ['classification__arrival_note__lot_id', 'species', 'custom_species_name', 'comment']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Informations', {
            'fields': ('classification', 'species', 'custom_species_name', 'weight', 'comment')
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at')
        }),
    )

    def get_species_name(self, obj):
        """Retourne le nom de l'espèce (personnalisé ou prédéfini)"""
        return obj.species_name
    get_species_name.short_description = 'Espèce'

    def get_queryset(self, request):
        """Optimise les requêtes en préchargeant les relations"""
        qs = super().get_queryset(request)
        return qs.select_related('classification', 'classification__arrival_note')
