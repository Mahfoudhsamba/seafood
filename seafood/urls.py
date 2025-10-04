from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about-us/', views.about_us, name='about_us'),
    path('contact/', views.contact, name='contact'),
    path('services/', views.services, name='services'),
    path('privacy/', views.privacy, name='privacy'),
    path('gallery/', views.gallery, name='gallery'),
    path('faqs/', views.faqs, name='faqs'),
    path('logistics/', views.logistics, name='logistics'),
    path('blog/', views.blog, name='blog'),
]