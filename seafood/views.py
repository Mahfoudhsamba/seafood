from django.shortcuts import render, get_object_or_404
from django.db import models
from django.http import JsonResponse
from portal.models import Product

def home(request):
    return render(request, 'seafood/home.html')


def about_us(request):
    return render(request, 'seafood/about-us.html')


def contact(request):
    return render(request, 'seafood/contact.html')


def products(request):
    # Récupérer tous les produits disponibles
    products_list = Product.objects.filter(is_available=True).select_related()

    # Filtrer par plusieurs catégories si spécifié
    categories = request.GET.getlist('category')
    if categories:
        products_list = products_list.filter(category__in=categories)

    # Recherche par mot-clé
    search_query = request.GET.get('search', '').strip()
    if search_query:
        products_list = products_list.filter(
            models.Q(product__icontains=search_query) |
            models.Q(local_name__icontains=search_query) |
            models.Q(scientific_name__icontains=search_query) |
            models.Q(description__icontains=search_query)
        )

    context = {
        'products': products_list,
        'selected_categories': categories,
        'categories': Product.CATEGORY_CHOICES,
        'search_query': search_query,
    }
    return render(request, 'seafood/products.html', context)


def product_detail(request, slug):
    # Récupérer le produit de manière sécurisée
    product = get_object_or_404(Product, slug=slug, is_available=True)

    # Récupérer les produits similaires de la même catégorie
    related_products = Product.objects.filter(
        category=product.category,
        is_available=True
    ).exclude(id=product.id)[:3]

    context = {
        'product': product,
        'related_products': related_products,
    }
    return render(request, 'seafood/product_detail.html', context)


def services(request):
    from portal.models import Service

    # Récupérer tous les services actifs
    services_list = Service.objects.filter(is_active=True).order_by('order', 'name')

    # Recherche par mot-clé
    search_query = request.GET.get('search', '').strip()
    if search_query:
        services_list = services_list.filter(
            models.Q(name__icontains=search_query) |
            models.Q(description__icontains=search_query)
        )

    context = {
        'services': services_list,
        'search_query': search_query,
    }
    return render(request, 'seafood/services.html', context)


def service_detail(request, slug):
    from portal.models import Service

    # Récupérer le service de manière sécurisée
    service = get_object_or_404(Service, slug=slug, is_active=True)

    # Récupérer les FAQs liées à ce service
    faqs = service.faqs.filter(is_active=True).order_by('order')

    # Récupérer d'autres services (max 3)
    other_services = Service.objects.filter(
        is_active=True
    ).exclude(id=service.id).order_by('order')[:3]

    context = {
        'service': service,
        'faqs': faqs,
        'other_services': other_services,
    }
    return render(request, 'seafood/service_detail.html', context)


def privacy(request):
    return render(request, 'seafood/privacy.html')


def gallery(request):
    from portal.models import Gallery

    # Récupérer toutes les images actives
    gallery_images = Gallery.objects.filter(is_active=True).order_by('order', '-created_at')

    # Recherche par mot-clé
    search_query = request.GET.get('search', '').strip()
    if search_query:
        gallery_images = gallery_images.filter(
            models.Q(title__icontains=search_query) |
            models.Q(description__icontains=search_query)
        )

    context = {
        'gallery_images': gallery_images,
        'search_query': search_query,
    }
    return render(request, 'seafood/gallery.html', context)


def faqs(request):
    from portal.models import FAQ, Service

    # Récupérer toutes les FAQs actives
    faqs_list = FAQ.objects.filter(is_active=True).select_related('service')

    # Filtrer par plusieurs services si spécifié
    services_ids = request.GET.getlist('service')
    if services_ids:
        faqs_list = faqs_list.filter(service_id__in=services_ids)

    # Recherche par mot-clé
    search_query = request.GET.get('search', '').strip()
    if search_query:
        faqs_list = faqs_list.filter(
            models.Q(question__icontains=search_query) |
            models.Q(answer__icontains=search_query)
        )

    # Récupérer tous les services actifs
    services_list = Service.objects.filter(is_active=True)

    context = {
        'faqs': faqs_list,
        'selected_services': services_ids,
        'services': services_list,
        'search_query': search_query,
    }
    return render(request, 'seafood/faqs.html', context)


def logistics(request):
    return render(request, 'seafood/logistics.html')


def blog(request):
    return render(request, 'seafood/blog.html')


def product_search_suggestions(request):
    """API pour les suggestions de recherche"""
    query = request.GET.get('q', '').strip()

    if len(query) < 2:
        return JsonResponse({'suggestions': []})

    # Rechercher dans les produits disponibles
    products = Product.objects.filter(
        is_available=True
    ).filter(
        models.Q(product__icontains=query) |
        models.Q(local_name__icontains=query) |
        models.Q(scientific_name__icontains=query)
    )[:5]  # Limiter à 5 suggestions

    suggestions = [
        {
            'id': p.id,
            'name': p.product,
            'local_name': p.local_name,
            'category': p.get_category_display(),
            'slug': p.slug
        }
        for p in products
    ]

    return JsonResponse({'suggestions': suggestions})
