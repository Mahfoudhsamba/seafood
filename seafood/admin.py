from django.contrib import admin
from django.contrib.admin import AdminSite
from django.urls import path
from . import views
from .models import Cashbox, BankAccount, PurchaseRequest, PurchaseRequestItem, PurchaseOrder, PurchaseOrderItem, CashboxTransaction

# Custom Portal Admin Site
class PortalAdminSite(AdminSite):
    site_header = 'Seafood Admin Portal'
    site_title = 'Seafood Admin'
    index_title = 'Tableau de Bord'

    def get_urls(self):
        from django.urls import path

        urls = super().get_urls()
        custom_urls = [
            path('', views.home, name='index'),
            path('login/', views.portal_login, name='login'),

            # Profile
            path('my-profile/', views.profile_view, name='profile'),
            path('my-profile/change-password/', views.password_change_view, name='profile_password_change'),

            # Clients
            path('clients/', views.client_list, name='client_list'),
            path('clients/add/', views.client_add, name='client_add'),
            path('clients/<int:pk>/', views.client_detail, name='client_detail'),
            path('clients/<int:pk>/edit/', views.client_edit, name='client_edit'),
            path('clients/<int:pk>/delete/', views.client_delete, name='client_delete'),

            # Suppliers
            path('suppliers/', views.supplier_list, name='supplier_list'),
            path('suppliers/add/', views.supplier_add, name='supplier_add'),
            path('suppliers/<int:pk>/', views.supplier_detail, name='supplier_detail'),
            path('suppliers/<int:pk>/edit/', views.supplier_edit, name='supplier_edit'),
            path('suppliers/<int:pk>/delete/', views.supplier_delete, name='supplier_delete'),

            # Cashbox
            path('cashbox/', views.cashbox_list, name='cashbox_list'),
            path('cashbox/add/', views.cashbox_add, name='cashbox_add'),
            path('cashbox/<int:pk>/', views.cashbox_detail, name='cashbox_detail'),
            path('cashbox/<int:pk>/edit/', views.cashbox_edit, name='cashbox_edit'),
            path('cashbox/<int:pk>/delete/', views.cashbox_delete, name='cashbox_delete'),
            path('cashbox/<int:cashbox_pk>/fund/', views.cashbox_fund, name='cashbox_fund'),
            path('cashbox/<int:cashbox_pk>/transactions/', views.cashbox_transactions, name='cashbox_transactions'),

            # Bank Account
            path('bankaccount/', views.bankaccount_list, name='bankaccount_list'),
            path('bankaccount/add/', views.bankaccount_add, name='bankaccount_add'),
            path('bankaccount/<int:pk>/', views.bankaccount_detail, name='bankaccount_detail'),
            path('bankaccount/<int:pk>/edit/', views.bankaccount_edit, name='bankaccount_edit'),
            path('bankaccount/<int:pk>/delete/', views.bankaccount_delete, name='bankaccount_delete'),

            # Purchase Request
            path('purchaserequest/', views.purchaserequest_list, name='purchaserequest_list'),
            path('purchaserequest/add/', views.purchaserequest_add, name='purchaserequest_add'),
            path('purchaserequest/<int:pk>/', views.purchaserequest_detail, name='purchaserequest_detail'),
            path('purchaserequest/<int:pk>/edit/', views.purchaserequest_edit, name='purchaserequest_edit'),
            path('purchaserequest/<int:pk>/approve/', views.purchaserequest_approve, name='purchaserequest_approve'),
            path('purchaserequest/<int:pk>/reject/', views.purchaserequest_reject, name='purchaserequest_reject'),
            path('purchaserequest/<int:pk>/delete/', views.purchaserequest_delete, name='purchaserequest_delete'),

            # Purchase Order
            path('purchaseorder/', views.purchaseorder_list, name='purchaseorder_list'),
            path('purchaseorder/add/', views.purchaseorder_add, name='purchaseorder_add'),
            path('purchaseorder/<int:pk>/', views.purchaseorder_detail, name='purchaseorder_detail'),
            path('purchaseorder/<int:pk>/edit/', views.purchaseorder_edit, name='purchaseorder_edit'),
            path('purchaseorder/<int:pk>/delete/', views.purchaseorder_delete, name='purchaseorder_delete'),
        ]
        return custom_urls + urls

# Create portal admin site instance
portal_admin_site = PortalAdminSite(name='portal_admin')

# Register your models here.

class CashboxAdmin(admin.ModelAdmin):
    list_display = ['folder_code', 'prefix', 'description', 'current_balance', 'created_at']
    list_filter = ['created_at']
    search_fields = ['folder_code', 'description']
    readonly_fields = ['created_at', 'updated_at', 'created_by']

    def save_model(self, request, obj, form, change):
        if not change:  # Si c'est une nouvelle instance
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


class BankAccountAdmin(admin.ModelAdmin):
    list_display = ['bank_identifier', 'bank_name', 'account_number', 'account_type', 'currency', 'status', 'current_balance']
    list_filter = ['status', 'account_type', 'category', 'currency', 'created_at']
    search_fields = ['bank_identifier', 'bank_name', 'account_number', 'iban', 'account_holder']
    readonly_fields = ['bank_identifier', 'created_at', 'updated_at', 'created_by']

    fieldsets = (
        ('Informations de base', {
            'fields': ('bank_identifier', 'bank_name', 'account_number', 'iban', 'agency')
        }),
        ('Type et catégorie', {
            'fields': ('account_type', 'category', 'currency', 'status')
        }),
        ('Contact et administratif', {
            'fields': ('account_holder', 'phone', 'email', 'address')
        }),
        ('Pièces jointes', {
            'fields': ('rib_scan', 'contract')
        }),
        ('Solde', {
            'fields': ('current_balance',)
        }),
        ('Dates', {
            'fields': ('account_opening_date', 'created_at', 'updated_at', 'created_by')
        }),
    )

    def save_model(self, request, obj, form, change):
        if not change:  # Si c'est une nouvelle instance
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


class PurchaseRequestAdmin(admin.ModelAdmin):
    list_display = ['pr_number', 'pr_date', 'requester_full_name', 'status', 'deadline']
    list_filter = ['status', 'pr_date', 'deadline', 'created_at']
    search_fields = ['pr_number', 'requester_first_name', 'requester_last_name', 'position']
    readonly_fields = ['pr_number', 'created_at', 'updated_at', 'created_by']

    fieldsets = (
        ('Informations PR', {
            'fields': ('pr_number', 'pr_date', 'description')
        }),
        ('Demandeur', {
            'fields': ('requester_first_name', 'requester_last_name', 'position', 'requester_phone')
        }),
        ('Échéance et statut', {
            'fields': ('deadline', 'status', 'rejection_reason')
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at', 'created_by')
        }),
    )

    def save_model(self, request, obj, form, change):
        if not change:  # Si c'est une nouvelle instance
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


class PurchaseRequestItemAdmin(admin.ModelAdmin):
    list_display = ['purchase_request', 'designation', 'quantity', 'unit', 'order']
    list_filter = ['unit']
    search_fields = ['designation', 'purchase_request__pr_number']

    fieldsets = (
        ('Article', {
            'fields': ('purchase_request', 'designation', 'quantity', 'unit', 'order')
        }),
    )


class PurchaseOrderItemInline(admin.TabularInline):
    model = PurchaseOrderItem
    extra = 1
    fields = ['designation', 'quantity', 'unit', 'unit_price', 'tax_rate', 'order']


class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = ['po_number', 'po_date', 'supplier', 'total', 'status', 'payment_date']
    list_filter = ['status', 'po_date', 'payment_date', 'created_at']
    search_fields = ['po_number', 'supplier__name', 'supplier__accounting_code']
    readonly_fields = ['po_number', 'subtotal', 'tax_amount', 'total', 'created_at', 'updated_at', 'created_by', 'approved_at']
    inlines = [PurchaseOrderItemInline]

    fieldsets = (
        ('Informations PO', {
            'fields': ('po_number', 'po_date', 'supplier')
        }),
        ('Totaux', {
            'fields': ('subtotal', 'tax_amount', 'total')
        }),
        ('Paiement', {
            'fields': ('payment_bank', 'payment_date', 'file')
        }),
        ('Statut et approbation', {
            'fields': ('status', 'approved_by', 'approved_at', 'note')
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at', 'created_by')
        }),
    )

    def save_model(self, request, obj, form, change):
        if not change:  # Si c'est une nouvelle instance
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


class PurchaseOrderItemAdmin(admin.ModelAdmin):
    list_display = ['purchase_order', 'designation', 'quantity', 'unit', 'unit_price', 'tax_rate', 'order']
    list_filter = ['unit']
    search_fields = ['designation', 'purchase_order__po_number']

    fieldsets = (
        ('Article', {
            'fields': ('purchase_order', 'designation', 'quantity', 'unit', 'unit_price', 'tax_rate', 'order')
        }),
    )


class CashboxTransactionAdmin(admin.ModelAdmin):
    list_display = ['transaction_number', 'cashbox', 'transaction_type', 'amount', 'transaction_date', 'balance_after', 'created_by']
    list_filter = ['transaction_type', 'source', 'transaction_date', 'created_at']
    search_fields = ['transaction_number', 'description', 'cashbox__folder_code']
    readonly_fields = ['transaction_number', 'balance_after', 'created_at', 'created_by']

    fieldsets = (
        ('Informations transaction', {
            'fields': ('transaction_number', 'cashbox', 'transaction_type', 'source', 'amount', 'transaction_date')
        }),
        ('Références', {
            'fields': ('bank_account',)
        }),
        ('Description', {
            'fields': ('description', 'justification')
        }),
        ('Solde', {
            'fields': ('balance_after',)
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'created_by')
        }),
    )

    def save_model(self, request, obj, form, change):
        if not change:  # Si c'est une nouvelle instance
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


# Register models on portal admin site
portal_admin_site.register(Cashbox, CashboxAdmin)
portal_admin_site.register(BankAccount, BankAccountAdmin)
portal_admin_site.register(PurchaseRequest, PurchaseRequestAdmin)
portal_admin_site.register(PurchaseRequestItem, PurchaseRequestItemAdmin)
portal_admin_site.register(PurchaseOrder, PurchaseOrderAdmin)
portal_admin_site.register(PurchaseOrderItem, PurchaseOrderItemAdmin)
portal_admin_site.register(CashboxTransaction, CashboxTransactionAdmin)
