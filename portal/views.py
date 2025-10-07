from django.shortcuts import render, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import authenticate, login
from django.contrib import messages
from .models import Product, Gallery, Service, FAQ

# Create your views here.

def portal_login(request):
    """Page de connexion du portail"""
    if request.user.is_authenticated:
        return redirect('portal_admin:index')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None and user.is_staff:
            login(request, user)
            next_url = request.GET.get('next', 'portal_admin:index')
            return redirect(next_url)
        else:
            messages.error(request, 'Nom d\'utilisateur ou mot de passe incorrect')

    return render(request, 'portal/auth/sign-in.html')

@staff_member_required
def home(request):
    """Page d'accueil du portail admin"""
    return render(request, 'portal/home.html')


# ============ PRODUCT VIEWS ============

@staff_member_required
def product_list(request):
    """Liste des produits"""
    products = Product.objects.all().order_by('-created_at')
    return render(request, 'portal/products/product_list.html', {'products': products})


@staff_member_required
def product_add(request):
    """Formulaire d'ajout de produit"""
    if request.method == 'POST':
        try:
            product = Product(
                product=request.POST.get('product'),
                local_name=request.POST.get('local_name', ''),
                scientific_name=request.POST.get('scientific_name', ''),
                image=request.FILES.get('image'),
                weight=request.POST.get('weight'),
                description=request.POST.get('description'),
                price=request.POST.get('price'),
                category=request.POST.get('category'),
                is_available=request.POST.get('is_available') == 'on',
                is_featured=request.POST.get('is_featured') == 'on',
                stock_quantity=request.POST.get('stock_quantity', 0),
                minimum_order=request.POST.get('minimum_order', 1.00)
            )
            product.save()
            messages.success(request, 'Produit ajouté avec succès!')
            return redirect('portal_admin:product_list')
        except Exception as e:
            messages.error(request, f'Erreur lors de l\'ajout: {str(e)}')

    return render(request, 'portal/products/product_form.html', {
        'categories': Product.CATEGORY_CHOICES
    })


# ============ GALLERY VIEWS ============

@staff_member_required
def gallery_list(request):
    """Liste des images de la galerie"""
    gallery_items = Gallery.objects.all().order_by('order', '-created_at')
    return render(request, 'portal/gallery/gallery_list.html', {'gallery_items': gallery_items})


@staff_member_required
def gallery_add(request):
    """Formulaire d'ajout d'image"""
    if request.method == 'POST':
        try:
            image = Gallery(
                image=request.FILES.get('image'),
                title=request.POST.get('title'),
                description=request.POST.get('description'),
                is_active=request.POST.get('is_active') == 'on',
                order=request.POST.get('order', 0)
            )
            image.save()
            messages.success(request, 'Image ajoutée avec succès!')
            return redirect('portal_admin:gallery_list')
        except Exception as e:
            messages.error(request, f'Erreur lors de l\'ajout: {str(e)}')

    return render(request, 'portal/gallery/gallery_form.html')


# ============ SERVICE VIEWS ============

@staff_member_required
def service_list(request):
    """Liste des services"""
    services = Service.objects.all().order_by('order', 'name')
    return render(request, 'portal/services/service_list.html', {'services': services})


@staff_member_required
def service_add(request):
    """Formulaire d'ajout de service"""
    if request.method == 'POST':
        try:
            service = Service(
                name=request.POST.get('name'),
                description=request.POST.get('description'),
                image=request.FILES.get('image') if 'image' in request.FILES else None,
                is_active=request.POST.get('is_active') == 'on',
                order=request.POST.get('order', 0)
            )
            service.save()
            messages.success(request, 'Service ajouté avec succès!')
            return redirect('portal_admin:service_list')
        except Exception as e:
            messages.error(request, f'Erreur lors de l\'ajout: {str(e)}')

    return render(request, 'portal/services/service_form.html')


# ============ FAQ VIEWS ============

@staff_member_required
def faq_list(request):
    """Liste des FAQs"""
    faqs = FAQ.objects.all().order_by('order', '-created_at')
    return render(request, 'portal/faq/faq_list.html', {'faqs': faqs})


@staff_member_required
def faq_add(request):
    """Formulaire d'ajout de FAQ"""
    if request.method == 'POST':
        try:
            faq = FAQ(
                question=request.POST.get('question'),
                answer=request.POST.get('answer'),
                service_id=request.POST.get('service') if request.POST.get('service') else None,
                order=request.POST.get('order', 0),
                is_active=request.POST.get('is_active') == 'on'
            )
            faq.save()
            messages.success(request, 'FAQ ajoutée avec succès!')
            return redirect('portal_admin:faq_list')
        except Exception as e:
            messages.error(request, f'Erreur lors de l\'ajout: {str(e)}')

    services = Service.objects.filter(is_active=True)
    return render(request, 'portal/faq/faq_form.html', {'services': services})
