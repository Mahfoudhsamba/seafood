from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import authenticate, login, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from .models import Product, Gallery, Service, FAQ, UserProfile

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


@staff_member_required
def product_edit(request, pk):
    """Formulaire de modification de produit"""
    from django.shortcuts import get_object_or_404
    product = get_object_or_404(Product, pk=pk)

    if request.method == 'POST':
        try:
            product.product = request.POST.get('product')
            product.local_name = request.POST.get('local_name', '')
            product.scientific_name = request.POST.get('scientific_name', '')
            if 'image' in request.FILES:
                product.image = request.FILES.get('image')
            product.weight = request.POST.get('weight')
            product.description = request.POST.get('description')
            product.price = request.POST.get('price')
            product.category = request.POST.get('category')
            product.is_available = request.POST.get('is_available') == 'on'
            product.is_featured = request.POST.get('is_featured') == 'on'
            product.stock_quantity = request.POST.get('stock_quantity', 0)
            product.minimum_order = request.POST.get('minimum_order', 1.00)
            product.save()
            messages.success(request, 'Produit modifié avec succès!')
            return redirect('portal_admin:product_list')
        except Exception as e:
            messages.error(request, f'Erreur lors de la modification: {str(e)}')

    return render(request, 'portal/products/product_form.html', {
        'product': product,
        'categories': Product.CATEGORY_CHOICES
    })


@staff_member_required
def product_delete(request, pk):
    """Suppression d'un produit"""
    from django.shortcuts import get_object_or_404
    product = get_object_or_404(Product, pk=pk)

    if request.method == 'POST':
        try:
            product.delete()
            messages.success(request, 'Produit supprimé avec succès!')
            return redirect('portal_admin:product_list')
        except Exception as e:
            messages.error(request, f'Erreur lors de la suppression: {str(e)}')

    return render(request, 'portal/products/product_confirm_delete.html', {
        'product': product
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


@staff_member_required
def gallery_edit(request, pk):
    """Formulaire de modification d'image"""
    from django.shortcuts import get_object_or_404
    gallery_item = get_object_or_404(Gallery, pk=pk)

    if request.method == 'POST':
        try:
            if 'image' in request.FILES:
                gallery_item.image = request.FILES.get('image')
            gallery_item.title = request.POST.get('title')
            gallery_item.description = request.POST.get('description')
            gallery_item.is_active = request.POST.get('is_active') == 'on'
            gallery_item.order = request.POST.get('order', 0)
            gallery_item.save()
            messages.success(request, 'Image modifiée avec succès!')
            return redirect('portal_admin:gallery_list')
        except Exception as e:
            messages.error(request, f'Erreur lors de la modification: {str(e)}')

    return render(request, 'portal/gallery/gallery_form.html', {
        'gallery_item': gallery_item
    })


@staff_member_required
def gallery_delete(request, pk):
    """Suppression d'une image"""
    from django.shortcuts import get_object_or_404
    gallery_item = get_object_or_404(Gallery, pk=pk)

    if request.method == 'POST':
        try:
            gallery_item.delete()
            messages.success(request, 'Image supprimée avec succès!')
            return redirect('portal_admin:gallery_list')
        except Exception as e:
            messages.error(request, f'Erreur lors de la suppression: {str(e)}')

    return render(request, 'portal/gallery/gallery_confirm_delete.html', {
        'gallery_item': gallery_item
    })


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


@staff_member_required
def service_edit(request, pk):
    """Formulaire de modification de service"""
    from django.shortcuts import get_object_or_404
    service = get_object_or_404(Service, pk=pk)

    if request.method == 'POST':
        try:
            service.name = request.POST.get('name')
            service.description = request.POST.get('description')
            if 'image' in request.FILES:
                service.image = request.FILES.get('image')
            service.is_active = request.POST.get('is_active') == 'on'
            service.order = request.POST.get('order', 0)
            service.save()
            messages.success(request, 'Service modifié avec succès!')
            return redirect('portal_admin:service_list')
        except Exception as e:
            messages.error(request, f'Erreur lors de la modification: {str(e)}')

    return render(request, 'portal/services/service_form.html', {
        'service': service
    })


@staff_member_required
def service_delete(request, pk):
    """Suppression d'un service"""
    from django.shortcuts import get_object_or_404
    service = get_object_or_404(Service, pk=pk)

    if request.method == 'POST':
        try:
            service.delete()
            messages.success(request, 'Service supprimé avec succès!')
            return redirect('portal_admin:service_list')
        except Exception as e:
            messages.error(request, f'Erreur lors de la suppression: {str(e)}')

    return render(request, 'portal/services/service_confirm_delete.html', {
        'service': service
    })


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


@staff_member_required
def faq_edit(request, pk):
    """Formulaire de modification de FAQ"""
    from django.shortcuts import get_object_or_404
    faq = get_object_or_404(FAQ, pk=pk)

    if request.method == 'POST':
        try:
            faq.question = request.POST.get('question')
            faq.answer = request.POST.get('answer')
            faq.service_id = request.POST.get('service') if request.POST.get('service') else None
            faq.order = request.POST.get('order', 0)
            faq.is_active = request.POST.get('is_active') == 'on'
            faq.save()
            messages.success(request, 'FAQ modifiée avec succès!')
            return redirect('portal_admin:faq_list')
        except Exception as e:
            messages.error(request, f'Erreur lors de la modification: {str(e)}')

    services = Service.objects.filter(is_active=True)
    return render(request, 'portal/faq/faq_form.html', {
        'faq': faq,
        'services': services
    })


@staff_member_required
def faq_delete(request, pk):
    """Suppression d'une FAQ"""
    from django.shortcuts import get_object_or_404
    faq = get_object_or_404(FAQ, pk=pk)

    if request.method == 'POST':
        try:
            faq.delete()
            messages.success(request, 'FAQ supprimée avec succès!')
            return redirect('portal_admin:faq_list')
        except Exception as e:
            messages.error(request, f'Erreur lors de la suppression: {str(e)}')

    return render(request, 'portal/faq/faq_confirm_delete.html', {
        'faq': faq
    })


# ============ PROFILE VIEWS ============

@staff_member_required
def profile_view(request):
    """Afficher et modifier le profil utilisateur"""
    user = request.user
    profile, created = UserProfile.objects.get_or_create(user=user)

    if request.method == 'POST':
        try:
            # Mettre à jour les informations de User
            user.first_name = request.POST.get('first_name', '')
            user.last_name = request.POST.get('last_name', '')
            user.email = request.POST.get('email', '')
            user.save()

            # Mettre à jour les informations de UserProfile
            profile.phone = request.POST.get('phone', '')
            profile.address = request.POST.get('address', '')
            profile.language = request.POST.get('language', 'fr')

            # Gérer l'avatar
            if 'avatar' in request.FILES:
                profile.avatar = request.FILES['avatar']

            profile.save()

            messages.success(request, 'Profil mis à jour avec succès!')
            return redirect('portal_admin:profile')
        except Exception as e:
            messages.error(request, f'Erreur lors de la mise à jour: {str(e)}')

    return render(request, 'portal/profile/profile.html', {
        'user': user,
        'profile': profile
    })


@staff_member_required
def password_change_view(request):
    """Changer le mot de passe"""
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important pour ne pas déconnecter l'utilisateur
            messages.success(request, 'Votre mot de passe a été changé avec succès!')
            return redirect('portal_admin:profile')
        else:
            for error in form.errors.values():
                messages.error(request, error)
    else:
        form = PasswordChangeForm(request.user)

    return render(request, 'portal/profile/password_change.html', {
        'form': form
    })
