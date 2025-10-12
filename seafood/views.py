from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import permission_required
from django.contrib.auth import authenticate, login, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from .models import UserProfile, Client, Supplier

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

    return render(request, 'seafood/auth/sign-in.html')

@staff_member_required
def home(request):
    """Page d'accueil du portail admin"""
    return render(request, 'seafood/home.html')


# ============ PROFILE VIEWS ============

@staff_member_required
def profile_view(request):
    """Afficher et modifier le profil utilisateur"""
    import os
    from django.core.files.base import ContentFile
    from authentication.models import User

    user = request.user
    profile, created = UserProfile.objects.get_or_create(user=user)

    if request.method == 'POST':
        try:
            # Récupérer l'ancien avatar avant toute modification
            old_avatar_path = None
            has_new_avatar = 'avatar' in request.FILES

            if has_new_avatar and user.avatar:
                old_avatar_path = user.avatar.path

            # Mettre à jour les informations de User
            user.first_name = request.POST.get('first_name', '')
            user.last_name = request.POST.get('last_name', '')
            user.email = request.POST.get('email', '')

            # Gérer l'avatar sur User (pas UserProfile)
            if has_new_avatar:
                uploaded_file = request.FILES['avatar']

                # Lire le contenu du fichier
                file_content = uploaded_file.read()

                # Créer le nouveau nom de fichier
                ext = uploaded_file.name.split('.')[-1].lower()
                new_filename = f"user_{user.id}.{ext}"
                new_path = os.path.join('media', 'avatars', new_filename)

                # Supprimer l'ancien fichier physique s'il existe
                if old_avatar_path and os.path.isfile(old_avatar_path):
                    try:
                        os.remove(old_avatar_path)
                    except Exception:
                        pass

                # Supprimer aussi le fichier cible s'il existe déjà
                if os.path.isfile(new_path):
                    try:
                        os.remove(new_path)
                    except Exception:
                        pass

                # Supprimer l'objet avatar de la base de données
                if user.avatar:
                    user.avatar.delete(save=False)

                # Sauvegarder avec le nouveau nom
                user.avatar.save(new_filename, ContentFile(file_content), save=False)

            user.save()

            # Mettre à jour les informations de UserProfile
            profile.phone = request.POST.get('phone', '')
            profile.address = request.POST.get('address', '')
            profile.language = request.POST.get('language', 'fr')
            profile.save()

            messages.success(request, 'Profil mis à jour avec succès!')
            return redirect('portal_admin:profile')
        except Exception as e:
            messages.error(request, f'Erreur lors de la mise à jour: {str(e)}')

    return render(request, 'seafood/profile/profile.html', {
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

    return render(request, 'seafood/profile/password_change.html', {
        'form': form
    })


# ============ CLIENT VIEWS ============

@staff_member_required
@permission_required('operations.view_client', raise_exception=True)
def client_list(request):
    """Liste des clients"""
    clients = Client.objects.all().order_by('-created_at')
    return render(request, 'seafood/clients/client_list.html', {'clients': clients})


@staff_member_required
@permission_required('operations.view_client', raise_exception=True)
def client_detail(request, pk):
    """Détails d'un client"""
    client = get_object_or_404(Client, pk=pk)
    return render(request, 'seafood/clients/client_detail.html', {'client': client})


@staff_member_required
@permission_required('operations.add_client', raise_exception=True)
def client_add(request):
    """Formulaire d'ajout de client"""
    if request.method == 'POST':
        try:
            import os
            from django.core.files.base import ContentFile

            # Sauvegarder d'abord sans logo pour obtenir l'ID
            uploaded_logo = request.FILES.get('logo') if 'logo' in request.FILES else None
            client = Client(
                name=request.POST.get('name'),
                client_type=request.POST.get('client_type'),
                website=request.POST.get('website', ''),
                responsible=request.POST.get('responsible', ''),
                mobile=request.POST.get('mobile', ''),
                phone=request.POST.get('phone', ''),
                email=request.POST.get('email', ''),
                address=request.POST.get('address', ''),
                city=request.POST.get('city', ''),
                postal_code=request.POST.get('postal_code', ''),
                country=request.POST.get('country', 'Mauritanie'),
                trade_register=request.POST.get('trade_register', ''),
                tax_id=request.POST.get('tax_id', ''),
                status=request.POST.get('status', 'active'),
                observations=request.POST.get('observations', '')
            )

            if uploaded_logo:
                # Lire le contenu du fichier
                file_content = uploaded_logo.read()
                ext = uploaded_logo.name.split('.')[-1].lower()

                # Sauvegarder temporairement
                client.logo.save(f'temp_{uploaded_logo.name}', ContentFile(file_content), save=False)

            client.save()

            # Maintenant renommer le logo avec l'ID
            if uploaded_logo:
                old_path = client.logo.path
                new_filename = f'client_{client.pk}.{ext}'

                # Supprimer l'ancien fichier
                if os.path.isfile(old_path):
                    os.remove(old_path)

                # Sauvegarder avec le bon nom
                client.logo.save(new_filename, ContentFile(file_content), save=True)

            messages.success(request, 'Client ajouté avec succès!')
            return redirect('portal_admin:client_list')
        except Exception as e:
            messages.error(request, f'Erreur lors de l\'ajout: {str(e)}')

    return render(request, 'seafood/clients/client_form.html', {
        'client_types': Client.CLIENT_TYPE_CHOICES,
        'statuses': Client.STATUS_CHOICES
    })


@staff_member_required
@permission_required('operations.change_client', raise_exception=True)
def client_edit(request, pk):
    """Formulaire de modification de client"""
    client = get_object_or_404(Client, pk=pk)

    if request.method == 'POST':
        try:
            import os
            from django.core.files.base import ContentFile

            client.name = request.POST.get('name')
            client.client_type = request.POST.get('client_type')
            client.website = request.POST.get('website', '')
            client.responsible = request.POST.get('responsible', '')
            client.mobile = request.POST.get('mobile', '')
            client.phone = request.POST.get('phone', '')
            client.email = request.POST.get('email', '')
            client.address = request.POST.get('address', '')
            client.city = request.POST.get('city', '')
            client.postal_code = request.POST.get('postal_code', '')
            client.country = request.POST.get('country', 'Mauritanie')
            client.trade_register = request.POST.get('trade_register', '')
            client.tax_id = request.POST.get('tax_id', '')
            client.status = request.POST.get('status', 'active')
            client.observations = request.POST.get('observations', '')

            if 'logo' in request.FILES:
                uploaded_logo = request.FILES.get('logo')
                file_content = uploaded_logo.read()
                ext = uploaded_logo.name.split('.')[-1].lower()
                new_filename = f'client_{client.pk}.{ext}'

                # Supprimer l'ancien logo si il existe
                if client.logo and os.path.isfile(client.logo.path):
                    os.remove(client.logo.path)

                # Sauvegarder avec le nouveau nom
                client.logo.save(new_filename, ContentFile(file_content), save=False)

            client.save()
            messages.success(request, 'Client modifié avec succès!')
            return redirect('portal_admin:client_list')
        except Exception as e:
            messages.error(request, f'Erreur lors de la modification: {str(e)}')

    return render(request, 'seafood/clients/client_form.html', {
        'client': client,
        'client_types': Client.CLIENT_TYPE_CHOICES,
        'statuses': Client.STATUS_CHOICES
    })


@staff_member_required
@permission_required('operations.delete_client', raise_exception=True)
def client_delete(request, pk):
    """Suppression d'un client"""
    client = get_object_or_404(Client, pk=pk)

    if request.method == 'POST':
        try:
            client.delete()
            messages.success(request, 'Client supprimé avec succès!')
            return redirect('portal_admin:client_list')
        except Exception as e:
            messages.error(request, f'Erreur lors de la suppression: {str(e)}')

    return render(request, 'seafood/clients/client_confirm_delete.html', {
        'client': client
    })


# ============ SUPPLIER VIEWS ============

@staff_member_required
@permission_required('seafood.view_supplier', raise_exception=True)
def supplier_list(request):
    """Liste des fournisseurs"""
    suppliers = Supplier.objects.all().order_by('-created_at')
    return render(request, 'seafood/suppliers/supplier_list.html', {'suppliers': suppliers})


@staff_member_required
@permission_required('seafood.view_supplier', raise_exception=True)
def supplier_detail(request, pk):
    """Détails d'un fournisseur"""
    supplier = get_object_or_404(Supplier, pk=pk)
    return render(request, 'seafood/suppliers/supplier_detail.html', {'supplier': supplier})


@staff_member_required
@permission_required('seafood.add_supplier', raise_exception=True)
def supplier_add(request):
    """Formulaire d'ajout de fournisseur"""
    if request.method == 'POST':
        try:
            import os
            from django.core.files.base import ContentFile

            # Sauvegarder d'abord sans logo pour obtenir l'ID
            uploaded_logo = request.FILES.get('logo') if 'logo' in request.FILES else None
            supplier = Supplier(
                name=request.POST.get('name'),
                category=request.POST.get('category'),
                tax_id=request.POST.get('tax_id', ''),
                trade_register=request.POST.get('trade_register', ''),
                payment_terms=request.POST.get('payment_terms', 30),
                contact_phone=request.POST.get('contact_phone', ''),
                mobile=request.POST.get('mobile', ''),
                email=request.POST.get('email', ''),
                website=request.POST.get('website', ''),
                address=request.POST.get('address', ''),
                city=request.POST.get('city', ''),
                country=request.POST.get('country', 'Mauritanie'),
                status=request.POST.get('status', 'active')
            )

            if uploaded_logo:
                # Lire le contenu du fichier
                file_content = uploaded_logo.read()
                ext = uploaded_logo.name.split('.')[-1].lower()

                # Sauvegarder temporairement
                supplier.logo.save(f'temp_{uploaded_logo.name}', ContentFile(file_content), save=False)

            supplier.save()

            # Maintenant renommer le logo avec l'ID
            if uploaded_logo:
                old_path = supplier.logo.path
                new_filename = f'supplier_{supplier.pk}.{ext}'

                # Supprimer l'ancien fichier
                if os.path.isfile(old_path):
                    os.remove(old_path)

                # Sauvegarder avec le bon nom
                supplier.logo.save(new_filename, ContentFile(file_content), save=True)

            messages.success(request, 'Fournisseur ajouté avec succès!')
            return redirect('portal_admin:supplier_list')
        except Exception as e:
            messages.error(request, f'Erreur lors de l\'ajout: {str(e)}')

    return render(request, 'seafood/suppliers/supplier_form.html', {
        'categories': Supplier.CATEGORY_CHOICES,
        'statuses': Supplier.STATUS_CHOICES
    })


@staff_member_required
@permission_required('seafood.change_supplier', raise_exception=True)
def supplier_edit(request, pk):
    """Formulaire de modification de fournisseur"""
    supplier = get_object_or_404(Supplier, pk=pk)

    if request.method == 'POST':
        try:
            import os
            from django.core.files.base import ContentFile

            supplier.name = request.POST.get('name')
            supplier.category = request.POST.get('category')
            supplier.tax_id = request.POST.get('tax_id', '')
            supplier.trade_register = request.POST.get('trade_register', '')
            supplier.payment_terms = request.POST.get('payment_terms', 30)
            supplier.contact_phone = request.POST.get('contact_phone', '')
            supplier.mobile = request.POST.get('mobile', '')
            supplier.email = request.POST.get('email', '')
            supplier.website = request.POST.get('website', '')
            supplier.address = request.POST.get('address', '')
            supplier.city = request.POST.get('city', '')
            supplier.country = request.POST.get('country', 'Mauritanie')
            supplier.status = request.POST.get('status', 'active')

            if 'logo' in request.FILES:
                uploaded_logo = request.FILES.get('logo')
                file_content = uploaded_logo.read()
                ext = uploaded_logo.name.split('.')[-1].lower()
                new_filename = f'supplier_{supplier.pk}.{ext}'

                # Supprimer l'ancien logo si il existe
                if supplier.logo and os.path.isfile(supplier.logo.path):
                    os.remove(supplier.logo.path)

                # Sauvegarder avec le nouveau nom
                supplier.logo.save(new_filename, ContentFile(file_content), save=False)

            supplier.save()
            messages.success(request, 'Fournisseur modifié avec succès!')
            return redirect('portal_admin:supplier_list')
        except Exception as e:
            messages.error(request, f'Erreur lors de la modification: {str(e)}')

    return render(request, 'seafood/suppliers/supplier_form.html', {
        'supplier': supplier,
        'categories': Supplier.CATEGORY_CHOICES,
        'statuses': Supplier.STATUS_CHOICES
    })


@staff_member_required
@permission_required('seafood.delete_supplier', raise_exception=True)
def supplier_delete(request, pk):
    """Suppression d'un fournisseur"""
    supplier = get_object_or_404(Supplier, pk=pk)

    if request.method == 'POST':
        try:
            supplier.delete()
            messages.success(request, 'Fournisseur supprimé avec succès!')
            return redirect('portal_admin:supplier_list')
        except Exception as e:
            messages.error(request, f'Erreur lors de la suppression: {str(e)}')

    return render(request, 'seafood/suppliers/supplier_confirm_delete.html', {
        'supplier': supplier
    })
