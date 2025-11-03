from django.contrib import admin
from .models import Service, ServiceCategory, ServiceSubCategory, FishCategory, Reception, Report, ReportItem, Classification, ClassificationItem

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


@admin.register(Reception)
class ReceptionAdmin(admin.ModelAdmin):
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


class ReportItemInline(admin.TabularInline):
    """
    Inline pour gérer les détails par espèce directement depuis le rapport
    """
    model = ReportItem
    extra = 1
    fields = ['species', 'custom_species_name', 'weight', 'comment']
    verbose_name = 'Détail par espèce'
    verbose_name_plural = 'Détails par espèce'


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ['arrival_note', 'report_date', 'status', 'get_total_weight', 'created_by']
    list_filter = ['status', 'report_date', 'created_at']
    search_fields = ['arrival_note__lot_id', 'arrival_note__client__name', 'general_observation']
    readonly_fields = ['report_date', 'created_at', 'updated_at', 'created_by']
    date_hierarchy = 'report_date'
    inlines = [ReportItemInline]

    fieldsets = (
        ('Informations principales', {
            'fields': ('arrival_note', 'report_date', 'status')
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


@admin.register(ReportItem)
class ReportItemAdmin(admin.ModelAdmin):
    list_display = ['report', 'get_species_name', 'weight', 'created_at']
    list_filter = ['species', 'created_at']
    search_fields = ['report__arrival_note__lot_id', 'species', 'custom_species_name', 'comment']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Informations', {
            'fields': ('report', 'species', 'custom_species_name', 'weight', 'comment')
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
        return qs.select_related('report', 'report__arrival_note')


@admin.register(ServiceSubCategory)
class ServiceSubCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'weight', 'price', 'status', 'created_at']
    list_filter = ['status', 'category', 'created_at']
    search_fields = ['name', 'description', 'category__name']
    readonly_fields = ['created_at', 'updated_at', 'created_by']

    fieldsets = (
        ('Informations de base', {
            'fields': ('category', 'name')
        }),
        ('Détails', {
            'fields': ('weight', 'price', 'description', 'status')
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


class ClassificationItemInline(admin.TabularInline):
    """
    Inline pour gérer les détails par espèce directement depuis la classification
    """
    model = ClassificationItem
    extra = 1
    fields = ['species', 'plate_count', 'weight']
    verbose_name = 'Détail de classification'
    verbose_name_plural = 'Détails de classification'
    raw_id_fields = ['species']


@admin.register(Classification)
class ClassificationAdmin(admin.ModelAdmin):
    list_display = ['reception', 'start_datetime', 'pointer_full_name', 'status', 'get_total_weight', 'get_total_plates', 'created_by']
    list_filter = ['status', 'start_datetime', 'created_at']
    search_fields = ['reception__lot_id', 'reception__client__name', 'pointer_full_name']
    readonly_fields = ['created_at', 'updated_at', 'created_by']
    date_hierarchy = 'start_datetime'
    inlines = [ClassificationItemInline]

    fieldsets = (
        ('Informations principales', {
            'fields': ('reception', 'pointer_full_name', 'status')
        }),
        ('Période de classification', {
            'fields': ('start_datetime', 'end_datetime')
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

    def get_total_plates(self, obj):
        """Retourne le nombre total de plats"""
        return obj.total_plates
    get_total_plates.short_description = 'Total plats'

    def save_model(self, request, obj, form, change):
        if not change:  # Si c'est une nouvelle instance
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        """Optimise les requêtes en préchargeant les relations"""
        qs = super().get_queryset(request)
        return qs.select_related('reception', 'reception__client', 'created_by').prefetch_related('items')


@admin.register(ClassificationItem)
class ClassificationItemAdmin(admin.ModelAdmin):
    list_display = ['classification', 'get_species_name', 'plate_count', 'weight', 'get_average_weight', 'created_at']
    list_filter = ['species__category', 'created_at']
    search_fields = ['classification__reception__lot_id', 'species__name']
    readonly_fields = ['created_at', 'updated_at']
    raw_id_fields = ['classification', 'species']

    fieldsets = (
        ('Informations', {
            'fields': ('classification', 'species', 'plate_count', 'weight')
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at')
        }),
    )

    def get_species_name(self, obj):
        """Retourne le nom de l'espèce"""
        return f"{obj.species.category.name} - {obj.species.name}"
    get_species_name.short_description = 'Espèce'

    def get_average_weight(self, obj):
        """Retourne le poids moyen par plat"""
        return f"{obj.average_weight_per_plate:.2f} kg"
    get_average_weight.short_description = 'Poids moyen/plat'

    def get_queryset(self, request):
        """Optimise les requêtes en préchargeant les relations"""
        qs = super().get_queryset(request)
        return qs.select_related('classification', 'classification__reception', 'species', 'species__category')
