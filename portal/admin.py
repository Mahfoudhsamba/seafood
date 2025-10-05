from django.contrib import admin
from django.utils.html import format_html
from .models import Gallery, Product, Service, FAQ

# Register your models here.

@admin.register(Gallery)
class GalleryAdmin(admin.ModelAdmin):
    list_display = ['title', 'image_preview', 'is_active', 'order', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['title', 'description']
    list_editable = ['is_active', 'order']
    ordering = ['order', '-created_at']

    fieldsets = (
        ('Informations principales', {
            'fields': ('title', 'description', 'image')
        }),
        ('Paramètres', {
            'fields': ('is_active', 'order')
        }),
    )

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover; border-radius: 5px;" />', obj.image.url)
        return '-'
    image_preview.short_description = 'Aperçu'


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['product', 'image_preview', 'category', 'price', 'weight', 'stock_status', 'is_featured', 'is_available']
    list_filter = ['category', 'is_available', 'is_featured', 'created_at']
    search_fields = ['product', 'local_name', 'scientific_name', 'description']
    list_editable = ['is_available', 'is_featured']
    prepopulated_fields = {'slug': ('product',)}
    readonly_fields = ['created_at', 'updated_at', 'get_total_price']

    fieldsets = (
        ('Informations générales', {
            'fields': ('product', 'slug', 'local_name', 'scientific_name', 'category')
        }),
        ('Image', {
            'fields': ('image',)
        }),
        ('Détails du produit', {
            'fields': ('description', 'weight', 'price', 'get_total_price')
        }),
        ('Stock et disponibilité', {
            'fields': ('stock_quantity', 'minimum_order', 'is_available', 'is_featured')
        }),
        ('Informations système', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="60" height="60" style="object-fit: cover; border-radius: 5px;" />', obj.image.url)
        return '-'
    image_preview.short_description = 'Image'

    def stock_status(self, obj):
        if obj.stock_quantity > 50:
            color = 'green'
            status = 'En stock'
        elif obj.stock_quantity > 0:
            color = 'orange'
            status = 'Stock faible'
        else:
            color = 'red'
            status = 'Rupture'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span> ({} kg)',
            color, status, obj.stock_quantity
        )
    stock_status.short_description = 'État du stock'

    def get_total_price(self, obj):
        if obj.pk:
            total = obj.get_total_price()
            return format_html('<strong>{:.2f} MRU</strong>', total)
        return '-'
    get_total_price.short_description = 'Prix total (poids × prix/kg)'

    actions = ['mark_as_featured', 'mark_as_not_featured', 'mark_as_available', 'mark_as_unavailable']

    def mark_as_featured(self, request, queryset):
        updated = queryset.update(is_featured=True)
        self.message_user(request, f'{updated} produit(s) marqué(s) comme vedette.')
    mark_as_featured.short_description = 'Marquer comme produit vedette'

    def mark_as_not_featured(self, request, queryset):
        updated = queryset.update(is_featured=False)
        self.message_user(request, f'{updated} produit(s) retiré(s) des produits vedettes.')
    mark_as_not_featured.short_description = 'Retirer des produits vedettes'

    def mark_as_available(self, request, queryset):
        updated = queryset.update(is_available=True)
        self.message_user(request, f'{updated} produit(s) marqué(s) comme disponible.')
    mark_as_available.short_description = 'Marquer comme disponible'

    def mark_as_unavailable(self, request, queryset):
        updated = queryset.update(is_available=False)
        self.message_user(request, f'{updated} produit(s) marqué(s) comme indisponible.')
    mark_as_unavailable.short_description = 'Marquer comme indisponible'


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'image_preview', 'is_active', 'order', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    list_editable = ['is_active', 'order']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['order', 'name']

    fieldsets = (
        ('Informations du service', {
            'fields': ('name', 'slug', 'description', 'image')
        }),
        ('Paramètres', {
            'fields': ('is_active', 'order')
        }),
    )

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover; border-radius: 5px;" />', obj.image.url)
        return '-'
    image_preview.short_description = 'Aperçu'


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ['question', 'service', 'is_active', 'order', 'created_at']
    list_filter = ['service', 'is_active', 'created_at']
    search_fields = ['question', 'answer']
    list_editable = ['is_active', 'order']
    ordering = ['order', '-created_at']

    fieldsets = (
        ('Question et Réponse', {
            'fields': ('question', 'answer', 'service')
        }),
        ('Paramètres', {
            'fields': ('is_active', 'order')
        }),
    )
