from django.contrib import admin
from django.contrib.admin import AdminSite
from django.urls import path
from . import views
from .models import Cashbox, BankAccount, PurchaseRequest, PurchaseRequestItem, PurchaseOrder, PurchaseOrderItem, CashboxTransaction, Prospect

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
            path('cashbox/<int:pk>/status/<str:new_status>/', views.cashbox_change_status, name='cashbox_change_status'),

            # Bank Account
            path('bankaccount/', views.bankaccount_list, name='bankaccount_list'),
            path('bankaccount/add/', views.bankaccount_add, name='bankaccount_add'),
            path('bankaccount/<int:pk>/', views.bankaccount_detail, name='bankaccount_detail'),
            path('bankaccount/<int:pk>/edit/', views.bankaccount_edit, name='bankaccount_edit'),
            path('bankaccount/<int:pk>/delete/', views.bankaccount_delete, name='bankaccount_delete'),
            path('bankaccount/<int:pk>/status/<str:new_status>/', views.bankaccount_change_status, name='bankaccount_change_status'),

            # Purchase Request
            path('purchaserequest/', views.purchaserequest_list, name='purchaserequest_list'),
            path('purchaserequest/add/', views.purchaserequest_add, name='purchaserequest_add'),
            path('purchaserequest/<int:pk>/', views.purchaserequest_detail, name='purchaserequest_detail'),
            path('purchaserequest/<int:pk>/edit/', views.purchaserequest_edit, name='purchaserequest_edit'),
            path('purchaserequest/<int:pk>/approve/', views.purchaserequest_approve, name='purchaserequest_approve'),
            path('purchaserequest/<int:pk>/reject/', views.purchaserequest_reject, name='purchaserequest_reject'),
            path('purchaserequest/<int:pk>/cancel/', views.purchaserequest_cancel, name='purchaserequest_cancel'),

            # Purchase Order
            path('purchaseorder/', views.purchaseorder_list, name='purchaseorder_list'),
            path('purchaseorder/add/', views.purchaseorder_add, name='purchaseorder_add'),
            path('purchaseorder/<int:pk>/', views.purchaseorder_detail, name='purchaseorder_detail'),
            path('purchaseorder/<int:pk>/edit/', views.purchaseorder_edit, name='purchaseorder_edit'),
            path('purchaseorder/<int:pk>/pending/', views.purchaseorder_pending, name='purchaseorder_pending'),
            path('purchaseorder/<int:pk>/approve/', views.purchaseorder_approve, name='purchaseorder_approve'),
            path('purchaseorder/<int:pk>/reject/', views.purchaseorder_reject, name='purchaseorder_reject'),
            path('purchaseorder/<int:pk>/pay/', views.purchaseorder_pay, name='purchaseorder_pay'),
            path('purchaseorder/<int:pk>/cancel/', views.purchaseorder_cancel, name='purchaseorder_cancel'),

            # Prospects
            path('prospects/', views.prospect_list, name='prospect_list'),
            path('prospects/add/', views.prospect_add, name='prospect_add'),
            path('prospects/<int:pk>/', views.prospect_detail, name='prospect_detail'),
            path('prospects/<int:pk>/edit/', views.prospect_edit, name='prospect_edit'),
            path('prospects/<int:pk>/delete/', views.prospect_delete, name='prospect_delete'),
            path('prospects/<int:pk>/status/<str:new_status>/', views.prospect_change_status, name='prospect_change_status'),

            # Reception (Notes d'Arrivée)
            path('reception/', views.arrivalnote_list, name='arrivalnote_list'),
            path('reception/add/', views.arrivalnote_add, name='arrivalnote_add'),
            path('reception/<int:pk>/', views.arrivalnote_detail, name='arrivalnote_detail'),
            path('reception/<int:pk>/edit/', views.arrivalnote_edit, name='arrivalnote_edit'),
            path('reception/<int:pk>/delete/', views.arrivalnote_delete, name='arrivalnote_delete'),
            path('reception/<int:pk>/change-status/', views.arrivalnote_change_status, name='arrivalnote_change_status'),

            # Services
            path('services/', views.service_list, name='service_list'),
            path('services/add/', views.service_add, name='service_add'),
            path('services/<int:pk>/', views.service_detail, name='service_detail'),
            path('services/<int:pk>/edit/', views.service_edit, name='service_edit'),
            path('services/<int:pk>/delete/', views.service_delete, name='service_delete'),
            path('services/<int:pk>/change-status/', views.service_change_status, name='service_change_status'),

            # Catégories de services
            path('service-categories/', views.servicecategory_list, name='servicecategory_list'),
            path('service-categories/add/', views.servicecategory_add, name='servicecategory_add'),
            path('service-categories/<int:pk>/', views.servicecategory_detail, name='servicecategory_detail'),
            path('service-categories/<int:pk>/edit/', views.servicecategory_edit, name='servicecategory_edit'),
            path('service-categories/<int:pk>/delete/', views.servicecategory_delete, name='servicecategory_delete'),
            path('service-categories/<int:pk>/change-status/', views.servicecategory_change_status, name='servicecategory_change_status'),

            # Rapports de réception
            path('rapports-reception/', views.reception_report_list, name='reception_report_list'),
            path('rapports-reception/add/', views.reception_report_add, name='reception_report_add'),
            path('rapports-reception/<int:pk>/', views.reception_report_detail, name='reception_report_detail'),
            path('rapports-reception/<int:pk>/edit/', views.reception_report_edit, name='reception_report_edit'),
            path('rapports-reception/<int:pk>/delete/', views.reception_report_delete, name='reception_report_delete'),
            path('rapports-reception/<int:pk>/change-status/', views.reception_report_change_status, name='reception_report_change_status'),
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


class ProspectAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'company_name', 'email', 'mobile', 'status', 'next_followup', 'created_at']
    list_filter = ['status', 'acquisition_source', 'contact_source', 'created_at', 'next_followup']
    search_fields = ['first_name', 'last_name', 'company_name', 'email', 'mobile']
    readonly_fields = ['created_at', 'updated_at', 'created_by']

    fieldsets = (
        ('Contact Person', {
            'fields': ('first_name', 'last_name', 'email', 'mobile', 'position', 'contact_source', 'status')
        }),
        ('Enterprise', {
            'fields': ('company_name', 'policy_maker', 'last_interaction', 'office_number', 'email_contact', 'website', 'address', 'city', 'zip_code', 'country')
        }),
        ('Social Media', {
            'fields': ('linkedin', 'twitter', 'facebook', 'instagram')
        }),
        ('Remark', {
            'fields': ('acquisition_source', 'trouble', 'remark')
        }),
        ('Meta data', {
            'fields': ('next_followup', 'created_at', 'updated_at', 'created_by')
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
portal_admin_site.register(Prospect, ProspectAdmin)
