from django.contrib import admin
from django.contrib.admin import AdminSite
from django.urls import path
from . import views

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
        ]
        return custom_urls + urls

# Create portal admin site instance
portal_admin_site = PortalAdminSite(name='portal_admin')

# Register your models here.
