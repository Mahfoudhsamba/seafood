from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about-us/', views.about_us, name='about_us'),
    path('contact/', views.contact, name='contact'),
    path('products/', views.products, name='products'),
    path('products/<slug:slug>/', views.product_detail, name='product_detail'),
    path('api/product-search/', views.product_search_suggestions, name='product_search_suggestions'),
    path('services/', views.services, name='services'),
    path('services/<slug:slug>/', views.service_detail, name='service_detail'),
    path('logistics/', views.logistics, name='logistics'),
    path('privacy/', views.privacy, name='privacy'),
    path('gallery/', views.gallery, name='gallery'),
    path('faqs/', views.faqs, name='faqs'),
    path('blog/', views.blog, name='blog'),
]