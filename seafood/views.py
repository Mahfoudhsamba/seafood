from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import permission_required
from django.contrib.auth import authenticate, login, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from .models import UserProfile, Client, Supplier, Cashbox, BankAccount, PurchaseRequest, PurchaseRequestItem, PurchaseOrder, PurchaseOrderItem, CashboxTransaction, Prospect
from operations.models import ArrivalNote, FishCategory, Service, ServiceCategory, Classification, ClassificationItem

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


# ============ CASHBOX VIEWS ============

@staff_member_required
@permission_required('seafood.view_cashbox', raise_exception=True)
def cashbox_list(request):
    """Liste des caisses"""
    cashboxes = Cashbox.objects.all().order_by('-created_at')
    return render(request, 'seafood/cashbox/cashbox_list.html', {'cashboxes': cashboxes})


@staff_member_required
@permission_required('seafood.view_cashbox', raise_exception=True)
def cashbox_detail(request, pk):
    """Détails d'une caisse"""
    from decimal import Decimal
    from django.db.models import Sum

    cashbox = get_object_or_404(Cashbox, pk=pk)
    transactions = CashboxTransaction.objects.filter(cashbox=cashbox).order_by('-transaction_date', '-created_at')

    # Calculer les totaux
    total_in = transactions.filter(transaction_type='in').aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    total_out = transactions.filter(transaction_type='out').aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

    return render(request, 'seafood/cashbox/cashbox_detail.html', {
        'cashbox': cashbox,
        'transactions': transactions,
        'total_in': total_in,
        'total_out': total_out
    })


@staff_member_required
@permission_required('seafood.add_cashbox', raise_exception=True)
def cashbox_add(request):
    """Formulaire d'ajout de caisse"""
    if request.method == 'POST':
        try:
            cashbox = Cashbox(
                folder_code=request.POST.get('folder_code'),
                prefix=request.POST.get('prefix'),
                description=request.POST.get('description', ''),
                status=request.POST.get('status', 'active'),
                current_balance=request.POST.get('current_balance', 0),
                created_by=request.user
            )
            cashbox.save()
            messages.success(request, 'Caisse ajoutée avec succès!')
            return redirect('portal_admin:cashbox_list')
        except Exception as e:
            messages.error(request, f'Erreur lors de l\'ajout: {str(e)}')

    return render(request, 'seafood/cashbox/cashbox_form.html', {
        'statuses': Cashbox.STATUS_CHOICES
    })


@staff_member_required
@permission_required('seafood.change_cashbox', raise_exception=True)
def cashbox_edit(request, pk):
    """Formulaire de modification de caisse"""
    cashbox = get_object_or_404(Cashbox, pk=pk)

    if request.method == 'POST':
        try:
            cashbox.folder_code = request.POST.get('folder_code')
            cashbox.prefix = request.POST.get('prefix')
            cashbox.description = request.POST.get('description', '')
            cashbox.status = request.POST.get('status', 'active')
            cashbox.current_balance = request.POST.get('current_balance', 0)
            cashbox.save()
            messages.success(request, 'Caisse modifiée avec succès!')
            return redirect('portal_admin:cashbox_list')
        except Exception as e:
            messages.error(request, f'Erreur lors de la modification: {str(e)}')

    return render(request, 'seafood/cashbox/cashbox_form.html', {
        'cashbox': cashbox,
        'statuses': Cashbox.STATUS_CHOICES
    })


@staff_member_required
@permission_required('seafood.delete_cashbox', raise_exception=True)
def cashbox_delete(request, pk):
    """Suppression d'une caisse"""
    cashbox = get_object_or_404(Cashbox, pk=pk)

    if request.method == 'POST':
        try:
            cashbox.delete()
            messages.success(request, 'Caisse supprimée avec succès!')
            return redirect('portal_admin:cashbox_list')
        except Exception as e:
            messages.error(request, f'Erreur lors de la suppression: {str(e)}')

    return render(request, 'seafood/cashbox/cashbox_confirm_delete.html', {'cashbox': cashbox})


@staff_member_required
@permission_required('seafood.change_cashbox', raise_exception=True)
def cashbox_change_status(request, pk, new_status):
    """Changer le statut d'une caisse"""
    cashbox = get_object_or_404(Cashbox, pk=pk)

    # Vérifier que le statut est valide
    valid_statuses = ['active', 'inactive', 'suspended']
    if new_status not in valid_statuses:
        messages.error(request, 'Statut invalide!')
        return redirect('portal_admin:cashbox_detail', pk=pk)

    # Messages selon le statut
    status_messages = {
        'active': 'Caisse activée avec succès!',
        'inactive': 'Caisse désactivée avec succès!',
        'suspended': 'Caisse suspendue avec succès!'
    }

    cashbox.status = new_status
    cashbox.save()
    messages.success(request, status_messages.get(new_status, 'Statut modifié avec succès!'))
    return redirect('portal_admin:cashbox_detail', pk=pk)


# ============ BANK ACCOUNT VIEWS ============

@staff_member_required
@permission_required('seafood.view_bankaccount', raise_exception=True)
def bankaccount_list(request):
    """Liste des comptes bancaires"""
    bankaccounts = BankAccount.objects.all().order_by('-created_at')
    return render(request, 'seafood/bankaccount/bankaccount_list.html', {'bankaccounts': bankaccounts})


@staff_member_required
@permission_required('seafood.view_bankaccount', raise_exception=True)
def bankaccount_detail(request, pk):
    """Détails d'un compte bancaire"""
    bankaccount = get_object_or_404(BankAccount, pk=pk)
    return render(request, 'seafood/bankaccount/bankaccount_detail.html', {'bankaccount': bankaccount})


@staff_member_required
@permission_required('seafood.add_bankaccount', raise_exception=True)
def bankaccount_add(request):
    """Formulaire d'ajout de compte bancaire"""
    if request.method == 'POST':
        try:
            import os
            from django.core.files.base import ContentFile

            rib_scan_file = request.FILES.get('rib_scan') if 'rib_scan' in request.FILES else None
            contract_file = request.FILES.get('contract') if 'contract' in request.FILES else None

            bankaccount = BankAccount(
                bank_name=request.POST.get('bank_name'),
                account_number=request.POST.get('account_number'),
                iban=request.POST.get('iban', ''),
                agency=request.POST.get('agency', ''),
                account_type=request.POST.get('account_type'),
                category=request.POST.get('category'),
                currency=request.POST.get('currency'),
                status=request.POST.get('status'),
                account_holder=request.POST.get('account_holder'),
                phone=request.POST.get('phone', ''),
                email=request.POST.get('email', ''),
                address=request.POST.get('address', ''),
                current_balance=request.POST.get('current_balance', 0),
                account_opening_date=request.POST.get('account_opening_date'),
                created_by=request.user
            )

            if rib_scan_file:
                bankaccount.rib_scan.save(rib_scan_file.name, rib_scan_file, save=False)
            if contract_file:
                bankaccount.contract.save(contract_file.name, contract_file, save=False)

            bankaccount.save()
            messages.success(request, 'Compte bancaire ajouté avec succès!')
            return redirect('portal_admin:bankaccount_list')
        except Exception as e:
            messages.error(request, f'Erreur lors de l\'ajout: {str(e)}')

    return render(request, 'seafood/bankaccount/bankaccount_form.html', {
        'account_types': BankAccount.ACCOUNT_TYPE_CHOICES,
        'categories': BankAccount.CATEGORY_CHOICES,
        'currencies': BankAccount.CURRENCY_CHOICES,
        'statuses': BankAccount.STATUS_CHOICES
    })


@staff_member_required
@permission_required('seafood.change_bankaccount', raise_exception=True)
def bankaccount_edit(request, pk):
    """Formulaire de modification de compte bancaire"""
    bankaccount = get_object_or_404(BankAccount, pk=pk)

    if request.method == 'POST':
        try:
            bankaccount.bank_name = request.POST.get('bank_name')
            bankaccount.account_number = request.POST.get('account_number')
            bankaccount.iban = request.POST.get('iban', '')
            bankaccount.agency = request.POST.get('agency', '')
            bankaccount.account_type = request.POST.get('account_type')
            bankaccount.category = request.POST.get('category')
            bankaccount.currency = request.POST.get('currency')
            bankaccount.status = request.POST.get('status')
            bankaccount.account_holder = request.POST.get('account_holder')
            bankaccount.phone = request.POST.get('phone', '')
            bankaccount.email = request.POST.get('email', '')
            bankaccount.address = request.POST.get('address', '')
            bankaccount.current_balance = request.POST.get('current_balance', 0)
            bankaccount.account_opening_date = request.POST.get('account_opening_date')

            if 'rib_scan' in request.FILES:
                if bankaccount.rib_scan:
                    bankaccount.rib_scan.delete(save=False)
                bankaccount.rib_scan = request.FILES['rib_scan']
            if 'contract' in request.FILES:
                if bankaccount.contract:
                    bankaccount.contract.delete(save=False)
                bankaccount.contract = request.FILES['contract']

            bankaccount.save()
            messages.success(request, 'Compte bancaire modifié avec succès!')
            return redirect('portal_admin:bankaccount_list')
        except Exception as e:
            messages.error(request, f'Erreur lors de la modification: {str(e)}')

    return render(request, 'seafood/bankaccount/bankaccount_form.html', {
        'bankaccount': bankaccount,
        'account_types': BankAccount.ACCOUNT_TYPE_CHOICES,
        'categories': BankAccount.CATEGORY_CHOICES,
        'currencies': BankAccount.CURRENCY_CHOICES,
        'statuses': BankAccount.STATUS_CHOICES
    })


@staff_member_required
@permission_required('seafood.delete_bankaccount', raise_exception=True)
def bankaccount_delete(request, pk):
    """Suppression d'un compte bancaire"""
    bankaccount = get_object_or_404(BankAccount, pk=pk)

    if request.method == 'POST':
        try:
            bankaccount.delete()
            messages.success(request, 'Compte bancaire supprimé avec succès!')
            return redirect('portal_admin:bankaccount_list')
        except Exception as e:
            messages.error(request, f'Erreur lors de la suppression: {str(e)}')

    return render(request, 'seafood/bankaccount/bankaccount_confirm_delete.html', {'bankaccount': bankaccount})


@staff_member_required
@permission_required('seafood.change_bankaccount', raise_exception=True)
def bankaccount_change_status(request, pk, new_status):
    """Changer le statut d'un compte bancaire"""
    bankaccount = get_object_or_404(BankAccount, pk=pk)

    # Vérifier que le statut est valide
    valid_statuses = ['active', 'inactive', 'closed', 'frozen']
    if new_status not in valid_statuses:
        messages.error(request, 'Statut invalide!')
        return redirect('portal_admin:bankaccount_detail', pk=pk)

    # Messages selon le statut
    status_messages = {
        'active': 'Compte bancaire activé avec succès!',
        'inactive': 'Compte bancaire désactivé avec succès!',
        'closed': 'Compte bancaire fermé avec succès!',
        'frozen': 'Compte bancaire gelé avec succès!'
    }

    bankaccount.status = new_status
    bankaccount.save()
    messages.success(request, status_messages.get(new_status, 'Statut modifié avec succès!'))
    return redirect('portal_admin:bankaccount_detail', pk=pk)


# ============ PURCHASE REQUEST VIEWS ============

@staff_member_required
@permission_required('seafood.view_purchaserequest', raise_exception=True)
def purchaserequest_list(request):
    """Liste des demandes d'achat"""
    purchase_requests = PurchaseRequest.objects.all().order_by('-pr_date', '-created_at')
    return render(request, 'seafood/purchaserequest/purchaserequest_list.html', {'purchase_requests': purchase_requests})


@staff_member_required
@permission_required('seafood.view_purchaserequest', raise_exception=True)
def purchaserequest_detail(request, pk):
    """Détails d'une demande d'achat"""
    purchase_request = get_object_or_404(PurchaseRequest, pk=pk)
    return render(request, 'seafood/purchaserequest/purchaserequest_detail.html', {'purchase_request': purchase_request})


@staff_member_required
@permission_required('seafood.add_purchaserequest', raise_exception=True)
def purchaserequest_add(request):
    """Formulaire d'ajout de demande d'achat"""
    if request.method == 'POST':
        try:
            from decimal import Decimal
            from datetime import date

            # Utiliser la date d'aujourd'hui automatiquement
            pr_date = date.today()

            # Créer le PR (toujours en status brouillon)
            purchase_request = PurchaseRequest(
                pr_date=pr_date,
                requester_first_name=request.POST.get('requester_first_name'),
                requester_last_name=request.POST.get('requester_last_name'),
                position=request.POST.get('position'),
                requester_phone=request.POST.get('requester_phone'),
                deadline=request.POST.get('deadline'),
                description=request.POST.get('description', ''),
                status='draft',  # Toujours brouillon à la création
                created_by=request.user
            )
            purchase_request.save()

            # Récupérer les lignes d'articles
            designations = request.POST.getlist('designation[]')
            quantities = request.POST.getlist('quantity[]')
            units = request.POST.getlist('unit[]')

            # Créer les items
            for i, designation in enumerate(designations):
                if designation.strip():  # Ignorer les lignes vides
                    PurchaseRequestItem.objects.create(
                        purchase_request=purchase_request,
                        designation=designation,
                        quantity=Decimal(quantities[i]),
                        unit=units[i],
                        order=i
                    )

            messages.success(request, 'Demande d\'achat ajoutée avec succès!')
            return redirect('portal_admin:purchaserequest_detail', pk=purchase_request.pk)
        except Exception as e:
            messages.error(request, f'Erreur lors de l\'ajout: {str(e)}')

    return render(request, 'seafood/purchaserequest/purchaserequest_form.html', {
        'units': PurchaseRequestItem.UNIT_CHOICES
    })


@staff_member_required
@permission_required('seafood.change_purchaserequest', raise_exception=True)
def purchaserequest_edit(request, pk):
    """Formulaire de modification de demande d'achat"""
    purchase_request = get_object_or_404(PurchaseRequest, pk=pk)

    # Ne permettre la modification que si le statut est brouillon
    if purchase_request.status != 'draft':
        messages.error(request, 'Seules les demandes en brouillon peuvent être modifiées!')
        return redirect('portal_admin:purchaserequest_detail', pk=pk)

    if request.method == 'POST':
        try:
            from decimal import Decimal

            # Ne pas modifier pr_date - il est défini automatiquement à la création
            purchase_request.requester_first_name = request.POST.get('requester_first_name')
            purchase_request.requester_last_name = request.POST.get('requester_last_name')
            purchase_request.position = request.POST.get('position')
            purchase_request.requester_phone = request.POST.get('requester_phone')
            purchase_request.deadline = request.POST.get('deadline')
            purchase_request.description = request.POST.get('description', '')
            purchase_request.save()

            # Supprimer les anciens items
            purchase_request.items.all().delete()

            # Recréer les items
            designations = request.POST.getlist('designation[]')
            quantities = request.POST.getlist('quantity[]')
            units = request.POST.getlist('unit[]')

            for i, designation in enumerate(designations):
                if designation.strip():
                    PurchaseRequestItem.objects.create(
                        purchase_request=purchase_request,
                        designation=designation,
                        quantity=Decimal(quantities[i]),
                        unit=units[i],
                        order=i
                    )

            messages.success(request, 'Demande d\'achat modifiée avec succès!')
            return redirect('portal_admin:purchaserequest_detail', pk=pk)
        except Exception as e:
            messages.error(request, f'Erreur lors de la modification: {str(e)}')

    return render(request, 'seafood/purchaserequest/purchaserequest_form.html', {
        'purchase_request': purchase_request,
        'units': PurchaseRequestItem.UNIT_CHOICES
    })


@staff_member_required
@permission_required('seafood.change_purchaserequest', raise_exception=True)
def purchaserequest_approve(request, pk):
    """Approuver une demande d'achat et créer le bon de commande"""
    from decimal import Decimal
    from datetime import date

    purchase_request = get_object_or_404(PurchaseRequest, pk=pk)

    if request.method == 'POST':
        try:
            # Récupérer le fournisseur
            supplier_id = request.POST.get('supplier')
            if not supplier_id:
                messages.error(request, 'Veuillez sélectionner un fournisseur!')
                return render(request, 'seafood/purchaserequest/purchaserequest_approve.html', {
                    'purchase_request': purchase_request,
                    'suppliers': Supplier.objects.filter(status='active')
                })

            # Récupérer tous les items de la PR
            items = purchase_request.items.all()

            if not items:
                messages.error(request, 'Aucun article trouvé dans cette demande d\'achat!')
                return redirect('portal_admin:purchaserequest_detail', pk=pk)

            # Valider que tous les prix sont renseignés
            for item in items:
                unit_price = request.POST.get(f'unit_price_{item.pk}')
                if not unit_price:
                    messages.error(request, f'Veuillez renseigner le prix unitaire pour l\'article: {item.designation}')
                    return render(request, 'seafood/purchaserequest/purchaserequest_approve.html', {
                        'purchase_request': purchase_request,
                        'suppliers': Supplier.objects.filter(status='active')
                    })

            # Créer le PO (en attente)
            purchase_order = PurchaseOrder(
                po_date=date.today(),
                supplier_id=supplier_id,
                status='pending',  # Créé en statut "En attente"
                note=f'Créé automatiquement depuis PR-{purchase_request.pr_number}',
                created_by=request.user
            )
            purchase_order.save()

            # Créer les items du PO
            for index, item in enumerate(items):
                unit_price = request.POST.get(f'unit_price_{item.pk}')
                tax_rate = request.POST.get(f'tax_rate_{item.pk}', '0')

                PurchaseOrderItem.objects.create(
                    purchase_order=purchase_order,
                    designation=item.designation,
                    quantity=item.quantity,
                    unit=item.unit,
                    unit_price=Decimal(unit_price),
                    tax_rate=Decimal(tax_rate),
                    order=index
                )

            # Calculer les totaux du PO
            purchase_order.calculate_totals()

            # Approuver la demande d'achat
            purchase_request.status = 'approved'
            purchase_request.rejection_reason = ''
            purchase_request.save()

            messages.success(
                request,
                f'Demande d\'achat approuvée avec succès! Bon de commande {purchase_order.po_number} créé avec {items.count()} article(s).'
            )
            return redirect('portal_admin:purchaseorder_detail', pk=purchase_order.pk)

        except Exception as e:
            messages.error(request, f'Erreur lors de l\'approbation: {str(e)}')
            return render(request, 'seafood/purchaserequest/purchaserequest_approve.html', {
                'purchase_request': purchase_request,
                'suppliers': Supplier.objects.filter(status='active')
            })

    # GET: Afficher le formulaire
    suppliers = Supplier.objects.filter(status='active')
    return render(request, 'seafood/purchaserequest/purchaserequest_approve.html', {
        'purchase_request': purchase_request,
        'suppliers': suppliers
    })


@staff_member_required
@permission_required('seafood.change_purchaserequest', raise_exception=True)
def purchaserequest_reject(request, pk):
    """Rejeter une demande d'achat"""
    purchase_request = get_object_or_404(PurchaseRequest, pk=pk)

    if request.method == 'POST':
        rejection_reason = request.POST.get('rejection_reason', '').strip()
        if not rejection_reason:
            messages.error(request, 'Le motif de rejet est obligatoire!')
            return render(request, 'seafood/purchaserequest/purchaserequest_reject.html', {'purchase_request': purchase_request})

        purchase_request.status = 'rejected'
        purchase_request.rejection_reason = rejection_reason
        purchase_request.save()
        messages.success(request, 'Demande d\'achat rejetée!')
        return redirect('portal_admin:purchaserequest_detail', pk=pk)

    return render(request, 'seafood/purchaserequest/purchaserequest_reject.html', {'purchase_request': purchase_request})


@staff_member_required
@permission_required('seafood.change_purchaserequest', raise_exception=True)
def purchaserequest_cancel(request, pk):
    """Annuler une demande d'achat"""
    purchase_request = get_object_or_404(PurchaseRequest, pk=pk)

    if request.method == 'POST':
        purchase_request.status = 'cancelled'
        purchase_request.save()
        messages.success(request, 'Demande d\'achat annulée!')
        return redirect('portal_admin:purchaserequest_detail', pk=pk)

    return render(request, 'seafood/purchaserequest/purchaserequest_cancel.html', {'purchase_request': purchase_request})


# ============ PURCHASE ORDER VIEWS ============

@staff_member_required
@permission_required('seafood.view_purchaseorder', raise_exception=True)
def purchaseorder_list(request):
    """Liste des bons de commande"""
    purchase_orders = PurchaseOrder.objects.all().order_by('-po_date', '-created_at')
    return render(request, 'seafood/purchaseorder/purchaseorder_list.html', {'purchase_orders': purchase_orders})


@staff_member_required
@permission_required('seafood.view_purchaseorder', raise_exception=True)
def purchaseorder_detail(request, pk):
    """Détails d'un bon de commande"""
    purchase_order = get_object_or_404(PurchaseOrder, pk=pk)
    return render(request, 'seafood/purchaseorder/purchaseorder_detail.html', {'purchase_order': purchase_order})


@staff_member_required
@permission_required('seafood.add_purchaseorder', raise_exception=True)
def purchaseorder_add(request):
    """Formulaire d'ajout de bon de commande"""
    if request.method == 'POST':
        try:
            from decimal import Decimal

            file = request.FILES.get('file') if 'file' in request.FILES else None

            # Créer le PO (toujours en brouillon)
            purchase_order = PurchaseOrder(
                po_date=request.POST.get('po_date'),
                supplier_id=request.POST.get('supplier'),
                note=request.POST.get('note', ''),
                status='draft',  # Toujours brouillon à la création
                created_by=request.user
            )

            if file:
                purchase_order.file.save(file.name, file, save=False)

            purchase_order.save()

            # Créer les items
            designations = request.POST.getlist('designation[]')
            quantities = request.POST.getlist('quantity[]')
            units = request.POST.getlist('unit[]')
            unit_prices = request.POST.getlist('unit_price[]')
            tax_rates = request.POST.getlist('tax_rate[]')

            for i, designation in enumerate(designations):
                if designation.strip():
                    PurchaseOrderItem.objects.create(
                        purchase_order=purchase_order,
                        designation=designation,
                        quantity=Decimal(quantities[i]),
                        unit=units[i],
                        unit_price=Decimal(unit_prices[i]),
                        tax_rate=Decimal(tax_rates[i]) if tax_rates[i] else Decimal('0.00'),
                        order=i
                    )

            # Calculer les totaux
            purchase_order.calculate_totals()

            messages.success(request, 'Bon de commande ajouté avec succès!')
            return redirect('portal_admin:purchaseorder_detail', pk=purchase_order.pk)
        except Exception as e:
            messages.error(request, f'Erreur lors de l\'ajout: {str(e)}')

    suppliers = Supplier.objects.filter(status='active')
    return render(request, 'seafood/purchaseorder/purchaseorder_form.html', {
        'suppliers': suppliers,
        'units': PurchaseOrderItem.UNIT_CHOICES
    })


@staff_member_required
@permission_required('seafood.change_purchaseorder', raise_exception=True)
def purchaseorder_edit(request, pk):
    """Formulaire de modification de bon de commande"""
    purchase_order = get_object_or_404(PurchaseOrder, pk=pk)

    # Ne permettre la modification que si le statut est brouillon
    if purchase_order.status != 'draft':
        messages.error(request, 'Seuls les bons de commande en brouillon peuvent être modifiés!')
        return redirect('portal_admin:purchaseorder_detail', pk=pk)

    if request.method == 'POST':
        try:
            from decimal import Decimal

            purchase_order.po_date = request.POST.get('po_date')
            purchase_order.payment_date = request.POST.get('payment_date') or None
            purchase_order.payment_bank_id = request.POST.get('payment_bank') or None
            purchase_order.supplier_id = request.POST.get('supplier')
            purchase_order.note = request.POST.get('note', '')
            purchase_order.status = request.POST.get('status')

            if 'file' in request.FILES:
                if purchase_order.file:
                    purchase_order.file.delete(save=False)
                purchase_order.file = request.FILES['file']

            purchase_order.save()

            # Supprimer les anciens items
            purchase_order.items.all().delete()

            # Créer les nouveaux items
            designations = request.POST.getlist('designation[]')
            quantities = request.POST.getlist('quantity[]')
            units = request.POST.getlist('unit[]')
            unit_prices = request.POST.getlist('unit_price[]')
            tax_rates = request.POST.getlist('tax_rate[]')

            for i, designation in enumerate(designations):
                if designation.strip():
                    PurchaseOrderItem.objects.create(
                        purchase_order=purchase_order,
                        designation=designation,
                        quantity=Decimal(quantities[i]),
                        unit=units[i],
                        unit_price=Decimal(unit_prices[i]),
                        tax_rate=Decimal(tax_rates[i]) if tax_rates[i] else Decimal('0.00'),
                        order=i
                    )

            # Recalculer les totaux
            purchase_order.calculate_totals()

            messages.success(request, 'Bon de commande modifié avec succès!')
            return redirect('portal_admin:purchaseorder_detail', pk=pk)
        except Exception as e:
            messages.error(request, f'Erreur lors de la modification: {str(e)}')

    suppliers = Supplier.objects.filter(status='active')
    bank_accounts = BankAccount.objects.filter(status='active')
    return render(request, 'seafood/purchaseorder/purchaseorder_form.html', {
        'purchase_order': purchase_order,
        'suppliers': suppliers,
        'bank_accounts': bank_accounts,
        'statuses': PurchaseOrder.STATUS_CHOICES,
        'units': PurchaseOrderItem.UNIT_CHOICES
    })


@staff_member_required
@permission_required('seafood.change_purchaseorder', raise_exception=True)
def purchaseorder_pending(request, pk):
    """Mettre un bon de commande en attente"""
    purchase_order = get_object_or_404(PurchaseOrder, pk=pk)

    if request.method == 'POST':
        purchase_order.status = 'pending'
        purchase_order.save()
        messages.success(request, 'Bon de commande mis en attente!')
        return redirect('portal_admin:purchaseorder_detail', pk=pk)

    return render(request, 'seafood/purchaseorder/purchaseorder_pending.html', {'purchase_order': purchase_order})


@staff_member_required
@permission_required('seafood.change_purchaseorder', raise_exception=True)
def purchaseorder_approve(request, pk):
    """Approuver un bon de commande"""
    purchase_order = get_object_or_404(PurchaseOrder, pk=pk)

    if request.method == 'POST':
        purchase_order.status = 'approved'
        purchase_order.approved_by = request.user
        from django.utils import timezone
        purchase_order.approved_at = timezone.now()
        purchase_order.save()
        messages.success(request, 'Bon de commande approuvé!')
        return redirect('portal_admin:purchaseorder_detail', pk=pk)

    return render(request, 'seafood/purchaseorder/purchaseorder_approve.html', {'purchase_order': purchase_order})


@staff_member_required
@permission_required('seafood.change_purchaseorder', raise_exception=True)
def purchaseorder_reject(request, pk):
    """Rejeter un bon de commande"""
    purchase_order = get_object_or_404(PurchaseOrder, pk=pk)

    if request.method == 'POST':
        rejection_reason = request.POST.get('rejection_reason', '').strip()
        if not rejection_reason:
            messages.error(request, 'Le motif de rejet est obligatoire!')
            return render(request, 'seafood/purchaseorder/purchaseorder_reject.html', {'purchase_order': purchase_order})

        purchase_order.status = 'cancelled'
        purchase_order.rejection_reason = rejection_reason
        purchase_order.save()
        messages.success(request, 'Bon de commande rejeté!')
        return redirect('portal_admin:purchaseorder_detail', pk=pk)

    return render(request, 'seafood/purchaseorder/purchaseorder_reject.html', {'purchase_order': purchase_order})


@staff_member_required
@permission_required('seafood.change_purchaseorder', raise_exception=True)
def purchaseorder_pay(request, pk):
    """Marquer un bon de commande comme payé"""
    from decimal import Decimal
    purchase_order = get_object_or_404(PurchaseOrder, pk=pk)

    if request.method == 'POST':
        from datetime import date

        payment_date = request.POST.get('payment_date')
        payment_method = request.POST.get('payment_method')
        payment_cashbox_id = request.POST.get('payment_cashbox') or None
        payment_bank_id = request.POST.get('payment_bank') or None

        # Validation
        if not payment_date:
            messages.error(request, 'La date de paiement est obligatoire!')
            bank_accounts = BankAccount.objects.filter(status='active')
            cashboxes = Cashbox.objects.all()
            return render(request, 'seafood/purchaseorder/purchaseorder_pay.html', {
                'purchase_order': purchase_order,
                'bank_accounts': bank_accounts,
                'cashboxes': cashboxes
            })

        if not payment_method:
            messages.error(request, 'La méthode de paiement est obligatoire!')
            bank_accounts = BankAccount.objects.filter(status='active')
            cashboxes = Cashbox.objects.all()
            return render(request, 'seafood/purchaseorder/purchaseorder_pay.html', {
                'purchase_order': purchase_order,
                'bank_accounts': bank_accounts,
                'cashboxes': cashboxes
            })

        if payment_method == 'cashbox' and not payment_cashbox_id:
            messages.error(request, 'Veuillez sélectionner une caisse!')
            bank_accounts = BankAccount.objects.filter(status='active')
            cashboxes = Cashbox.objects.all()
            return render(request, 'seafood/purchaseorder/purchaseorder_pay.html', {
                'purchase_order': purchase_order,
                'bank_accounts': bank_accounts,
                'cashboxes': cashboxes
            })

        if payment_method == 'bank' and not payment_bank_id:
            messages.error(request, 'Veuillez sélectionner un compte bancaire!')
            bank_accounts = BankAccount.objects.filter(status='active')
            cashboxes = Cashbox.objects.all()
            return render(request, 'seafood/purchaseorder/purchaseorder_pay.html', {
                'purchase_order': purchase_order,
                'bank_accounts': bank_accounts,
                'cashboxes': cashboxes
            })

        # Vérifier que le crédit est suffisant selon la méthode de paiement
        if payment_method == 'cashbox':
            cashbox = get_object_or_404(Cashbox, pk=payment_cashbox_id)
            if cashbox.current_balance < purchase_order.total:
                messages.error(request, f'Solde insuffisant dans la caisse! Solde disponible: {cashbox.current_balance} MRU, Montant requis: {purchase_order.total} MRU')
                bank_accounts = BankAccount.objects.filter(status='active')
                cashboxes = Cashbox.objects.all()
                return render(request, 'seafood/purchaseorder/purchaseorder_pay.html', {
                    'purchase_order': purchase_order,
                    'bank_accounts': bank_accounts,
                    'cashboxes': cashboxes
                })
        elif payment_method == 'bank':
            bank_account = get_object_or_404(BankAccount, pk=payment_bank_id)
            if bank_account.current_balance < purchase_order.total:
                messages.error(request, f'Solde insuffisant dans le compte bancaire! Solde disponible: {bank_account.current_balance} MRU, Montant requis: {purchase_order.total} MRU')
                bank_accounts = BankAccount.objects.filter(status='active')
                cashboxes = Cashbox.objects.all()
                return render(request, 'seafood/purchaseorder/purchaseorder_pay.html', {
                    'purchase_order': purchase_order,
                    'bank_accounts': bank_accounts,
                    'cashboxes': cashboxes
                })

        # Mettre à jour le PO
        purchase_order.status = 'paid'
        purchase_order.payment_date = payment_date
        purchase_order.payment_method = payment_method
        purchase_order.payment_cashbox_id = payment_cashbox_id
        purchase_order.payment_bank_id = payment_bank_id

        if 'file' in request.FILES:
            if purchase_order.file:
                purchase_order.file.delete(save=False)
            purchase_order.file = request.FILES['file']

        purchase_order.save()

        # Décrémenter le solde selon la méthode de paiement
        if payment_method == 'cashbox':
            # Créer une transaction de sortie pour la caisse
            cashbox = get_object_or_404(Cashbox, pk=payment_cashbox_id)
            transaction = CashboxTransaction(
                cashbox=cashbox,
                transaction_type='out',
                source='purchase_order',
                amount=purchase_order.total,
                transaction_date=payment_date,
                description=f'Paiement du bon de commande {purchase_order.po_number} - {purchase_order.supplier.name}',
                created_by=request.user
            )
            transaction.save()
            # Le solde de la caisse est automatiquement décrémenté par le signal du modèle CashboxTransaction
        elif payment_method == 'bank':
            # Décrémenter le solde du compte bancaire
            bank_account = get_object_or_404(BankAccount, pk=payment_bank_id)
            bank_account.current_balance -= purchase_order.total
            bank_account.save()

        messages.success(request, 'Bon de commande marqué comme payé!')
        return redirect('portal_admin:purchaseorder_detail', pk=pk)

    bank_accounts = BankAccount.objects.filter(status='active')
    cashboxes = Cashbox.objects.all()
    return render(request, 'seafood/purchaseorder/purchaseorder_pay.html', {
        'purchase_order': purchase_order,
        'bank_accounts': bank_accounts,
        'cashboxes': cashboxes
    })


@staff_member_required
@permission_required('seafood.change_purchaseorder', raise_exception=True)
def purchaseorder_cancel(request, pk):
    """Annuler un bon de commande"""
    purchase_order = get_object_or_404(PurchaseOrder, pk=pk)

    if request.method == 'POST':
        purchase_order.status = 'cancelled'
        purchase_order.save()
        messages.success(request, 'Bon de commande annulé!')
        return redirect('portal_admin:purchaseorder_detail', pk=pk)

    return render(request, 'seafood/purchaseorder/purchaseorder_cancel.html', {'purchase_order': purchase_order})


# ============ CASHBOX TRANSACTION VIEWS ============

@staff_member_required
@permission_required('seafood.add_cashboxtransaction', raise_exception=True)
def cashbox_fund(request, cashbox_pk):
    """Formulaire d'alimentation de caisse"""
    from decimal import Decimal
    cashbox = get_object_or_404(Cashbox, pk=cashbox_pk)

    if request.method == 'POST':
        try:
            source = request.POST.get('source')

            transaction = CashboxTransaction(
                cashbox=cashbox,
                transaction_type='in',
                source=source,
                amount=Decimal(request.POST.get('amount')),
                transaction_date=request.POST.get('transaction_date'),
                description=request.POST.get('description'),
                created_by=request.user
            )

            # Champs spécifiques selon le mode de paiement
            if source == 'mobile_transfer':
                transaction.transaction_id = request.POST.get('transaction_id', '')
                transaction.issuing_bank_id = request.POST.get('issuing_bank') or None
            elif source in ['check', 'deposit']:
                transaction.check_number = request.POST.get('check_number', '')
                transaction.issuing_bank_id = request.POST.get('issuing_bank') or None
                transaction.check_date = request.POST.get('check_date') or None
            elif source == 'bank_transfer':
                transaction.transfer_reference = request.POST.get('transfer_reference', '')
                transaction.issuing_bank_id = request.POST.get('issuing_bank') or None
                transaction.check_date = request.POST.get('check_date') or None

            if 'justification' in request.FILES:
                transaction.justification = request.FILES['justification']

            transaction.save()
            messages.success(request, 'Caisse alimentée avec succès!')
            return redirect('portal_admin:cashbox_detail', pk=cashbox_pk)
        except Exception as e:
            messages.error(request, f'Erreur lors de l\'alimentation: {str(e)}')

    bank_accounts = BankAccount.objects.filter(status='active')
    return render(request, 'seafood/cashbox/cashbox_fund.html', {
        'cashbox': cashbox,
        'bank_accounts': bank_accounts,
        'sources': CashboxTransaction.SOURCE_CHOICES
    })


# ============ PROSPECT VIEWS ============

@staff_member_required
@permission_required('seafood.view_prospect', raise_exception=True)
def prospect_list(request):
    """Liste des prospects"""
    prospects = Prospect.objects.all().order_by('-created_at')

    # Filtrage par statut
    status_filter = request.GET.get('status')
    if status_filter:
        prospects = prospects.filter(status=status_filter)

    # Recherche
    search = request.GET.get('search')
    if search:
        from django.db.models import Q
        prospects = prospects.filter(
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search) |
            Q(company_name__icontains=search) |
            Q(email__icontains=search)
        )

    return render(request, 'seafood/prospects/prospect_list.html', {
        'prospects': prospects,
        'statuses': Prospect.STATUS_CHOICES
    })


@staff_member_required
@permission_required('seafood.view_prospect', raise_exception=True)
def prospect_detail(request, pk):
    """Détails d'un prospect"""
    prospect = get_object_or_404(Prospect, pk=pk)
    return render(request, 'seafood/prospects/prospect_detail.html', {'prospect': prospect})


@staff_member_required
@permission_required('seafood.add_prospect', raise_exception=True)
def prospect_add(request):
    """Formulaire d'ajout de prospect"""
    if request.method == 'POST':
        try:
            prospect = Prospect(
                # Contact Person
                first_name=request.POST.get('first_name'),
                last_name=request.POST.get('last_name'),
                email=request.POST.get('email'),
                mobile=request.POST.get('mobile'),
                position=request.POST.get('position'),
                contact_source=request.POST.get('contact_source'),
                status=request.POST.get('status', 'new'),

                # Enterprise
                company_name=request.POST.get('company_name'),
                policy_maker=request.POST.get('policy_maker', ''),
                last_interaction=request.POST.get('last_interaction') or None,
                office_number=request.POST.get('office_number', ''),
                email_contact=request.POST.get('email_contact', ''),
                website=request.POST.get('website', ''),
                zip_code=request.POST.get('zip_code', ''),
                city=request.POST.get('city', ''),
                country=request.POST.get('country', 'Mauritanie'),
                address=request.POST.get('address', ''),

                # Social Media
                linkedin=request.POST.get('linkedin', ''),
                twitter=request.POST.get('twitter', ''),
                facebook=request.POST.get('facebook', ''),
                instagram=request.POST.get('instagram', ''),

                # Remark
                acquisition_source=request.POST.get('acquisition_source'),
                trouble=request.POST.get('trouble', ''),
                remark=request.POST.get('remark', ''),

                # Meta data
                next_followup=request.POST.get('next_followup') or None,
                created_by=request.user
            )
            prospect.save()
            messages.success(request, 'Prospect ajouté avec succès!')
            return redirect('portal_admin:prospect_detail', pk=prospect.pk)
        except Exception as e:
            messages.error(request, f'Erreur lors de l\'ajout: {str(e)}')

    return render(request, 'seafood/prospects/prospect_form.html', {
        'statuses': Prospect.STATUS_CHOICES,
        'sources': Prospect.SOURCE_CHOICES
    })


@staff_member_required
@permission_required('seafood.change_prospect', raise_exception=True)
def prospect_edit(request, pk):
    """Formulaire de modification de prospect"""
    prospect = get_object_or_404(Prospect, pk=pk)

    if request.method == 'POST':
        try:
            # Contact Person
            prospect.first_name = request.POST.get('first_name')
            prospect.last_name = request.POST.get('last_name')
            prospect.email = request.POST.get('email')
            prospect.mobile = request.POST.get('mobile')
            prospect.position = request.POST.get('position')
            prospect.contact_source = request.POST.get('contact_source')
            prospect.status = request.POST.get('status', 'new')

            # Enterprise
            prospect.company_name = request.POST.get('company_name')
            prospect.policy_maker = request.POST.get('policy_maker', '')
            prospect.last_interaction = request.POST.get('last_interaction') or None
            prospect.office_number = request.POST.get('office_number', '')
            prospect.email_contact = request.POST.get('email_contact', '')
            prospect.website = request.POST.get('website', '')
            prospect.zip_code = request.POST.get('zip_code', '')
            prospect.city = request.POST.get('city', '')
            prospect.country = request.POST.get('country', 'Mauritanie')
            prospect.address = request.POST.get('address', '')

            # Social Media
            prospect.linkedin = request.POST.get('linkedin', '')
            prospect.twitter = request.POST.get('twitter', '')
            prospect.facebook = request.POST.get('facebook', '')
            prospect.instagram = request.POST.get('instagram', '')

            # Remark
            prospect.acquisition_source = request.POST.get('acquisition_source')
            prospect.trouble = request.POST.get('trouble', '')
            prospect.remark = request.POST.get('remark', '')

            # Meta data
            prospect.next_followup = request.POST.get('next_followup') or None

            prospect.save()
            messages.success(request, 'Prospect modifié avec succès!')
            return redirect('portal_admin:prospect_detail', pk=pk)
        except Exception as e:
            messages.error(request, f'Erreur lors de la modification: {str(e)}')

    return render(request, 'seafood/prospects/prospect_form.html', {
        'prospect': prospect,
        'statuses': Prospect.STATUS_CHOICES,
        'sources': Prospect.SOURCE_CHOICES
    })


@staff_member_required
@permission_required('seafood.delete_prospect', raise_exception=True)
def prospect_delete(request, pk):
    """Suppression d'un prospect"""
    prospect = get_object_or_404(Prospect, pk=pk)

    if request.method == 'POST':
        try:
            prospect.delete()
            messages.success(request, 'Prospect supprimé avec succès!')
            return redirect('portal_admin:prospect_list')
        except Exception as e:
            messages.error(request, f'Erreur lors de la suppression: {str(e)}')

    return render(request, 'seafood/prospects/prospect_confirm_delete.html', {'prospect': prospect})


@staff_member_required
@permission_required('seafood.change_prospect', raise_exception=True)
def prospect_change_status(request, pk, new_status):
    """Changer le statut d'un prospect"""
    prospect = get_object_or_404(Prospect, pk=pk)

    # Vérifier que le statut est valide
    valid_statuses = ['new', 'contacted', 'qualified', 'relaunched', 'converted', 'lost']
    if new_status not in valid_statuses:
        messages.error(request, 'Statut invalide!')
        return redirect('portal_admin:prospect_detail', pk=pk)

    # Messages selon le statut
    status_messages = {
        'new': 'Prospect marqué comme nouveau!',
        'contacted': 'Prospect marqué comme contacté!',
        'qualified': 'Prospect qualifié!',
        'relaunched': 'Prospect relancé!',
        'converted': 'Prospect converti en client!',
        'lost': 'Prospect marqué comme perdu!'
    }

    prospect.status = new_status
    prospect.save()
    messages.success(request, status_messages.get(new_status, 'Statut modifié avec succès!'))
    return redirect('portal_admin:prospect_detail', pk=pk)


# ============ ARRIVAL NOTE VIEWS (Notes d'Arrivée) ============

@staff_member_required
@permission_required('operations.view_arrivalnote', raise_exception=True)
def arrivalnote_list(request):
    """Liste des notes d'arrivée"""
    arrival_notes = ArrivalNote.objects.all().select_related('client', 'service_type__category', 'created_by').order_by('-created_at')

    # Filtrage par statut
    status_filter = request.GET.get('status')
    if status_filter:
        arrival_notes = arrival_notes.filter(status=status_filter)

    # Filtrage par service
    service_filter = request.GET.get('service')
    if service_filter:
        arrival_notes = arrival_notes.filter(service_type_id=service_filter)

    # Recherche
    search = request.GET.get('search')
    if search:
        from django.db.models import Q
        arrival_notes = arrival_notes.filter(
            Q(lot_id__icontains=search) |
            Q(client__name__icontains=search) |
            Q(client__accounting_code__icontains=search)
        )

    return render(request, 'operations/reception/reception_list.html', {
        'arrival_notes': arrival_notes,
        'statuses': ArrivalNote.STATUS_CHOICES,
        'services': Service.objects.filter(status='active').order_by('code')
    })


@staff_member_required
@permission_required('operations.view_arrivalnote', raise_exception=True)
def arrivalnote_detail(request, pk):
    """Détails d'une note d'arrivée"""
    arrival_note = get_object_or_404(ArrivalNote.objects.select_related('client', 'service_type__category', 'created_by'), pk=pk)
    return render(request, 'operations/reception/reception_detail.html', {
        'arrival_note': arrival_note,
        'status_choices': ArrivalNote.STATUS_CHOICES
    })


@staff_member_required
@permission_required('operations.add_arrivalnote', raise_exception=True)
def arrivalnote_add(request):
    """Formulaire d'ajout de note d'arrivée"""
    if request.method == 'POST':
        try:
            from datetime import date

            arrival_note = ArrivalNote(
                client_id=request.POST.get('client'),
                reception_date=request.POST.get('reception_date') or date.today(),
                weight=request.POST.get('weight'),
                service_type_id=request.POST.get('service_type'),
                observations=request.POST.get('observations', ''),
                created_by=request.user
            )
            arrival_note.save()
            messages.success(request, f'Note d\'arrivée créée avec succès! LOT: {arrival_note.lot_id}')
            return redirect('portal_admin:arrivalnote_detail', pk=arrival_note.pk)
        except Exception as e:
            messages.error(request, f'Erreur lors de l\'ajout: {str(e)}')

    clients = Client.objects.filter(status='active').order_by('name')
    services = Service.objects.filter(status='active').order_by('code')

    return render(request, 'operations/reception/reception_form.html', {
        'clients': clients,
        'services': services
    })


@staff_member_required
@permission_required('operations.change_arrivalnote', raise_exception=True)
def arrivalnote_edit(request, pk):
    """Formulaire de modification de note d'arrivée"""
    arrival_note = get_object_or_404(ArrivalNote, pk=pk)

    # Ne permettre la modification que si le statut est 'draft'
    if arrival_note.status != 'draft':
        messages.error(request, 'Seules les notes d\'arrivée en statut "Brouillon" peuvent être modifiées!')
        return redirect('portal_admin:arrivalnote_detail', pk=pk)

    if request.method == 'POST':
        try:
            arrival_note.client_id = request.POST.get('client')
            arrival_note.reception_date = request.POST.get('reception_date')
            arrival_note.weight = request.POST.get('weight')
            arrival_note.service_type_id = request.POST.get('service_type')
            arrival_note.observations = request.POST.get('observations', '')
            arrival_note.save()

            messages.success(request, 'Note d\'arrivée modifiée avec succès!')
            return redirect('portal_admin:arrivalnote_detail', pk=pk)
        except Exception as e:
            messages.error(request, f'Erreur lors de la modification: {str(e)}')

    clients = Client.objects.filter(status='active').order_by('name')
    services = Service.objects.filter(status='active').order_by('code')

    return render(request, 'operations/reception/reception_form.html', {
        'arrival_note': arrival_note,
        'clients': clients,
        'services': services
    })


@staff_member_required
@permission_required('operations.delete_arrivalnote', raise_exception=True)
def arrivalnote_delete(request, pk):
    """Suppression d'une note d'arrivée"""
    arrival_note = get_object_or_404(ArrivalNote, pk=pk)

    if request.method == 'POST':
        try:
            lot_id = arrival_note.lot_id
            arrival_note.delete()
            messages.success(request, f'Note d\'arrivée LOT {lot_id} supprimée avec succès!')
            return redirect('portal_admin:arrivalnote_list')
        except Exception as e:
            messages.error(request, f'Erreur lors de la suppression: {str(e)}')

    return render(request, 'operations/reception/reception_confirm_delete.html', {'arrival_note': arrival_note})


@staff_member_required
@permission_required('operations.change_arrivalnote', raise_exception=True)
def arrivalnote_change_status(request, pk):
    """Changer le statut d'une note d'arrivée"""
    arrival_note = get_object_or_404(ArrivalNote, pk=pk)

    if request.method == 'POST':
        new_status = request.POST.get('status')

        # Vérifier que le nouveau statut est valide
        valid_statuses = [choice[0] for choice in ArrivalNote.STATUS_CHOICES]
        if new_status not in valid_statuses:
            messages.error(request, 'Statut invalide!')
            return redirect('portal_admin:arrivalnote_detail', pk=pk)

        # Vérifier les règles de changement de statut
        if arrival_note.status == 'accepted' and new_status != arrival_note.status:
            # Une fois accepté, on peut seulement passer à 'in_progress', 'suspended' ou 'cancelled'
            if new_status not in ['in_progress', 'suspended', 'cancelled']:
                messages.error(request, 'Changement de statut non autorisé. Un lot accepté ne peut passer qu\'en traitement, suspendu ou annulé.')
                return redirect('portal_admin:arrivalnote_detail', pk=pk)

        if arrival_note.status == 'in_progress' and new_status not in ['completed', 'suspended', 'cancelled', 'in_progress']:
            messages.error(request, 'Un lot en traitement ne peut passer qu\'à terminé, suspendu ou annulé.')
            return redirect('portal_admin:arrivalnote_detail', pk=pk)

        if arrival_note.status == 'completed':
            messages.error(request, 'Un lot terminé ne peut plus changer de statut.')
            return redirect('portal_admin:arrivalnote_detail', pk=pk)

        # Appliquer le changement
        old_status = arrival_note.get_status_display()
        arrival_note.status = new_status
        arrival_note.save()

        new_status_display = arrival_note.get_status_display()
        messages.success(request, f'Statut changé de "{old_status}" à "{new_status_display}"')
        return redirect('portal_admin:arrivalnote_detail', pk=pk)

    return redirect('portal_admin:arrivalnote_detail', pk=pk)


# ======================
# SERVICE VIEWS
# ======================

@staff_member_required
@permission_required('operations.view_service', raise_exception=True)
def service_list(request):
    """Liste des services"""
    services = Service.objects.all().select_related('created_by', 'category').order_by('code')

    # Filtrage par statut
    status_filter = request.GET.get('status')
    if status_filter:
        services = services.filter(status=status_filter)

    # Filtrage par catégorie
    category_filter = request.GET.get('category')
    if category_filter:
        services = services.filter(category_id=category_filter)

    # Recherche
    search = request.GET.get('search')
    if search:
        from django.db.models import Q
        services = services.filter(
            Q(code__icontains=search) |
            Q(name__icontains=search) |
            Q(description__icontains=search)
        )

    return render(request, 'operations/services/service_list.html', {
        'services': services,
        'statuses': Service.STATUS_CHOICES,
        'categories': ServiceCategory.objects.filter(status='active').order_by('name')
    })


@staff_member_required
@permission_required('operations.view_service', raise_exception=True)
def service_detail(request, pk):
    """Détails d'un service"""
    service = get_object_or_404(Service, pk=pk)
    return render(request, 'operations/services/service_detail.html', {
        'service': service,
        'status_choices': Service.STATUS_CHOICES
    })


@staff_member_required
@permission_required('operations.add_service', raise_exception=True)
def service_add(request):
    """Formulaire d'ajout de service"""
    if request.method == 'POST':
        try:
            # Récupérer le code
            code = request.POST.get('code', '').strip()

            # Si l'utilisateur choisit "auto", laisser le système générer
            if code == 'auto' or not code:
                code = 'auto'

            service = Service(
                code=code,
                name=request.POST.get('name'),
                category_id=request.POST.get('category'),
                description=request.POST.get('description', ''),
                amount=request.POST.get('amount', 0),
                status=request.POST.get('status', 'active'),
                created_by=request.user
            )
            service.save()
            messages.success(request, f'Service {service.code} - {service.name} créé avec succès!')
            return redirect('portal_admin:service_detail', pk=service.pk)
        except Exception as e:
            messages.error(request, f'Erreur lors de la création du service: {str(e)}')

    # Récupérer uniquement les codes réservés (1000-1010) disponibles
    reserved_codes = []
    for code in range(1000, 1011):
        code_str = str(code)
        is_used = Service.objects.filter(code=code_str).exists()
        # N'ajouter que les codes disponibles (non utilisés)
        if not is_used:
            reserved_codes.append(code_str)

    # Récupérer les catégories actives
    categories = ServiceCategory.objects.filter(status='active').order_by('name')

    return render(request, 'operations/services/service_form.html', {
        'categories': categories,
        'statuses': Service.STATUS_CHOICES,
        'reserved_codes': reserved_codes,
    })


@staff_member_required
@permission_required('operations.change_service', raise_exception=True)
def service_edit(request, pk):
    """Formulaire de modification de service"""
    service = get_object_or_404(Service, pk=pk)

    if request.method == 'POST':
        try:
            service.name = request.POST.get('name')
            service.category_id = request.POST.get('category')
            service.description = request.POST.get('description', '')
            service.amount = request.POST.get('amount', 0)
            service.status = request.POST.get('status', 'active')

            # Ne pas permettre la modification du code pour éviter les conflits
            # Le code reste fixe après création

            service.save()
            messages.success(request, f'Service {service.code} - {service.name} modifié avec succès!')
            return redirect('portal_admin:service_detail', pk=service.pk)
        except Exception as e:
            messages.error(request, f'Erreur lors de la modification du service: {str(e)}')

    # Récupérer les catégories actives
    categories = ServiceCategory.objects.filter(status='active').order_by('name')

    return render(request, 'operations/services/service_form.html', {
        'service': service,
        'categories': categories,
        'statuses': Service.STATUS_CHOICES,
    })


@staff_member_required
@permission_required('operations.delete_service', raise_exception=True)
def service_delete(request, pk):
    """Suppression d'un service"""
    service = get_object_or_404(Service, pk=pk)

    if request.method == 'POST':
        try:
            code = service.code
            name = service.name
            service.delete()
            messages.success(request, f'Service {code} - {name} supprimé avec succès!')
            return redirect('portal_admin:service_list')
        except Exception as e:
            messages.error(request, f'Erreur lors de la suppression: {str(e)}')

    return render(request, 'operations/services/service_confirm_delete.html', {'service': service})


@staff_member_required
@permission_required('operations.change_service', raise_exception=True)
def service_change_status(request, pk):
    """Changer le statut d'un service"""
    service = get_object_or_404(Service, pk=pk)

    if request.method == 'POST':
        new_status = request.POST.get('status')

        # Vérifier que le nouveau statut est valide
        valid_statuses = [choice[0] for choice in Service.STATUS_CHOICES]
        if new_status not in valid_statuses:
            messages.error(request, 'Statut invalide!')
            return redirect('portal_admin:service_detail', pk=pk)

        # Appliquer le changement
        old_status = service.get_status_display()
        service.status = new_status
        service.save()

        new_status_display = service.get_status_display()
        messages.success(request, f'Statut du service changé de "{old_status}" à "{new_status_display}"')
        return redirect('portal_admin:service_detail', pk=pk)

    return redirect('portal_admin:service_detail', pk=pk)


# ======================
# SERVICE CATEGORY VIEWS
# ======================

@staff_member_required
@permission_required('operations.view_servicecategory', raise_exception=True)
def servicecategory_list(request):
    """Liste des catégories de services"""
    categories = ServiceCategory.objects.all().select_related('created_by').order_by('name')

    # Filtrage par statut
    status_filter = request.GET.get('status')
    if status_filter:
        categories = categories.filter(status=status_filter)

    # Recherche
    search = request.GET.get('search')
    if search:
        from django.db.models import Q
        categories = categories.filter(
            Q(name__icontains=search) |
            Q(description__icontains=search)
        )

    return render(request, 'operations/service_categories/servicecategory_list.html', {
        'categories': categories,
        'statuses': ServiceCategory.STATUS_CHOICES
    })


@staff_member_required
@permission_required('operations.view_servicecategory', raise_exception=True)
def servicecategory_detail(request, pk):
    """Détails d'une catégorie de service"""
    category = get_object_or_404(ServiceCategory, pk=pk)
    return render(request, 'operations/service_categories/servicecategory_detail.html', {
        'category': category,
        'status_choices': ServiceCategory.STATUS_CHOICES
    })


@staff_member_required
@permission_required('operations.add_servicecategory', raise_exception=True)
def servicecategory_add(request):
    """Formulaire d'ajout de catégorie de service"""
    if request.method == 'POST':
        try:
            import os
            from django.core.files.base import ContentFile

            uploaded_avatar = request.FILES.get('avatar') if 'avatar' in request.FILES else None

            category = ServiceCategory(
                name=request.POST.get('name'),
                description=request.POST.get('description', ''),
                status=request.POST.get('status', 'active'),
                created_by=request.user
            )

            if uploaded_avatar:
                file_content = uploaded_avatar.read()
                ext = uploaded_avatar.name.split('.')[-1].lower()
                category.avatar.save(f'temp_{uploaded_avatar.name}', ContentFile(file_content), save=False)

            category.save()

            # Renommer l'avatar avec l'ID
            if uploaded_avatar:
                old_path = category.avatar.path
                new_filename = f'service_category_{category.pk}.{ext}'

                if os.path.isfile(old_path):
                    os.remove(old_path)

                category.avatar.save(new_filename, ContentFile(file_content), save=True)

            messages.success(request, f'Catégorie "{category.name}" créée avec succès!')
            return redirect('portal_admin:servicecategory_detail', pk=category.pk)
        except Exception as e:
            messages.error(request, f'Erreur lors de la création: {str(e)}')

    return render(request, 'operations/service_categories/servicecategory_form.html', {
        'statuses': ServiceCategory.STATUS_CHOICES,
    })


@staff_member_required
@permission_required('operations.change_servicecategory', raise_exception=True)
def servicecategory_edit(request, pk):
    """Formulaire de modification de catégorie de service"""
    category = get_object_or_404(ServiceCategory, pk=pk)

    if request.method == 'POST':
        try:
            import os
            from django.core.files.base import ContentFile

            category.name = request.POST.get('name')
            category.description = request.POST.get('description', '')
            category.status = request.POST.get('status', 'active')

            if 'avatar' in request.FILES:
                uploaded_avatar = request.FILES.get('avatar')
                file_content = uploaded_avatar.read()
                ext = uploaded_avatar.name.split('.')[-1].lower()
                new_filename = f'service_category_{category.pk}.{ext}'

                # Supprimer l'ancien avatar s'il existe
                if category.avatar and os.path.isfile(category.avatar.path):
                    os.remove(category.avatar.path)

                category.avatar.save(new_filename, ContentFile(file_content), save=False)

            category.save()
            messages.success(request, f'Catégorie "{category.name}" modifiée avec succès!')
            return redirect('portal_admin:servicecategory_detail', pk=category.pk)
        except Exception as e:
            messages.error(request, f'Erreur lors de la modification: {str(e)}')

    return render(request, 'operations/service_categories/servicecategory_form.html', {
        'category': category,
        'statuses': ServiceCategory.STATUS_CHOICES,
    })


@staff_member_required
@permission_required('operations.delete_servicecategory', raise_exception=True)
def servicecategory_delete(request, pk):
    """Suppression d'une catégorie de service"""
    category = get_object_or_404(ServiceCategory, pk=pk)

    if request.method == 'POST':
        try:
            name = category.name
            category.delete()
            messages.success(request, f'Catégorie "{name}" supprimée avec succès!')
            return redirect('portal_admin:servicecategory_list')
        except Exception as e:
            messages.error(request, f'Erreur lors de la suppression: {str(e)}')

    return render(request, 'operations/service_categories/servicecategory_confirm_delete.html', {'category': category})


@staff_member_required
@permission_required('operations.change_servicecategory', raise_exception=True)
def servicecategory_change_status(request, pk):
    """Changer le statut d'une catégorie de service"""
    category = get_object_or_404(ServiceCategory, pk=pk)

    if request.method == 'POST':
        new_status = request.POST.get('status')

        # Vérifier que le nouveau statut est valide
        valid_statuses = [choice[0] for choice in ServiceCategory.STATUS_CHOICES]
        if new_status not in valid_statuses:
            messages.error(request, 'Statut invalide!')
            return redirect('portal_admin:servicecategory_detail', pk=pk)

        # Appliquer le changement
        old_status = category.get_status_display()
        category.status = new_status
        category.save()

        new_status_display = category.get_status_display()
        messages.success(request, f'Statut de la catégorie changé de "{old_status}" à "{new_status_display}"')
        return redirect('portal_admin:servicecategory_detail', pk=pk)

    return redirect('portal_admin:servicecategory_detail', pk=pk)


# ============ RAPPORTS DE RÉCEPTION ============

@staff_member_required
@permission_required('operations.view_classification', raise_exception=True)
def reception_report_list(request):
    """Liste des rapports de réception"""
    classifications = Classification.objects.all().select_related(
        'arrival_note',
        'arrival_note__client',
        'arrival_note__service_type',
        'created_by'
    ).prefetch_related('items').order_by('-classification_date')

    return render(request, 'operations/reception_reports/report_list.html', {
        'classifications': classifications
    })


@staff_member_required
@permission_required('operations.view_classification', raise_exception=True)
def reception_report_detail(request, pk):
    """Détails d'un rapport de réception"""
    classification = get_object_or_404(
        Classification.objects.select_related(
            'arrival_note',
            'arrival_note__client',
            'arrival_note__service_type',
            'created_by'
        ).prefetch_related('items'),
        pk=pk
    )

    return render(request, 'operations/reception_reports/report_detail.html', {
        'classification': classification,
        'status_choices': Classification.STATUS_CHOICES
    })


@staff_member_required
@permission_required('operations.add_classification', raise_exception=True)
def reception_report_add(request):
    """Formulaire d'ajout de rapport de réception"""
    if request.method == 'POST':
        try:
            import json

            # Créer le rapport de réception
            arrival_note_id = request.POST.get('arrival_note')
            arrival_note = get_object_or_404(ArrivalNote, pk=arrival_note_id)

            classification = Classification.objects.create(
                arrival_note=arrival_note,
                general_observation=request.POST.get('general_observation', ''),
                status='draft',
                created_by=request.user
            )

            # Récupérer les items depuis le formulaire
            items_data = request.POST.get('items_data', '[]')
            items = json.loads(items_data)

            # Créer les détails par espèce
            for item in items:
                if item.get('species') and item.get('weight'):
                    ClassificationItem.objects.create(
                        classification=classification,
                        species=item['species'],
                        custom_species_name=item.get('custom_species_name', ''),
                        weight=item['weight'],
                        comment=item.get('comment', '')
                    )

            messages.success(request, f'Rapport de réception pour le LOT {arrival_note.lot_id} créé avec succès!')
            return redirect('portal_admin:reception_report_detail', pk=classification.pk)

        except Exception as e:
            messages.error(request, f'Erreur lors de la création: {str(e)}')

    # Récupérer les lots éligibles (service_type.code > '1003')
    # Exclure les lots qui ont déjà un rapport de réception
    # Seuls les lots acceptés peuvent avoir un rapport
    eligible_lots = ArrivalNote.objects.filter(
        service_type__code__gt='1003',
        classifications__isnull=True,
        status='accepted'
    ).select_related('client', 'service_type').order_by('-reception_date')

    return render(request, 'operations/reception_reports/report_form.html', {
        'eligible_lots': eligible_lots,
        'species_choices': ClassificationItem.SPECIES_CHOICES,
        'status_choices': Classification.STATUS_CHOICES
    })


@staff_member_required
@permission_required('operations.change_classification', raise_exception=True)
def reception_report_edit(request, pk):
    """Formulaire de modification de rapport de réception"""
    classification = get_object_or_404(
        Classification.objects.select_related('arrival_note', 'arrival_note__client').prefetch_related('items'),
        pk=pk
    )

    # Vérifier si le rapport peut être modifié
    if not classification.can_be_edited:
        messages.error(request, 'Ce rapport ne peut plus être modifié car il est validé ou annulé.')
        return redirect('portal_admin:reception_report_detail', pk=pk)

    if request.method == 'POST':
        try:
            import json

            # Mettre à jour le rapport
            classification.general_observation = request.POST.get('general_observation', '')
            classification.status = request.POST.get('status', 'draft')
            classification.save()

            # Supprimer les anciens items
            classification.items.all().delete()

            # Récupérer et créer les nouveaux items
            items_data = request.POST.get('items_data', '[]')
            items = json.loads(items_data)

            for item in items:
                if item.get('species') and item.get('weight'):
                    ClassificationItem.objects.create(
                        classification=classification,
                        species=item['species'],
                        custom_species_name=item.get('custom_species_name', ''),
                        weight=item['weight'],
                        comment=item.get('comment', '')
                    )

            messages.success(request, 'Rapport de réception modifié avec succès!')
            return redirect('portal_admin:reception_report_detail', pk=classification.pk)

        except Exception as e:
            messages.error(request, f'Erreur lors de la modification: {str(e)}')

    # Récupérer les lots éligibles
    eligible_lots = ArrivalNote.objects.filter(
        service_type__code__gt='1003'
    ).select_related('client', 'service_type').order_by('-reception_date')

    return render(request, 'operations/reception_reports/report_form.html', {
        'classification': classification,
        'eligible_lots': eligible_lots,
        'species_choices': ClassificationItem.SPECIES_CHOICES,
        'status_choices': Classification.STATUS_CHOICES
    })


@staff_member_required
@permission_required('operations.delete_classification', raise_exception=True)
def reception_report_delete(request, pk):
    """Suppression d'un rapport de réception"""
    classification = get_object_or_404(
        Classification.objects.select_related('arrival_note'),
        pk=pk
    )

    if request.method == 'POST':
        try:
            lot_id = classification.arrival_note.lot_id
            classification.delete()
            messages.success(request, f'Rapport de réception pour le LOT {lot_id} supprimé avec succès!')
            return redirect('portal_admin:reception_report_list')
        except Exception as e:
            messages.error(request, f'Erreur lors de la suppression: {str(e)}')

    return render(request, 'operations/reception_reports/report_confirm_delete.html', {
        'classification': classification
    })


@staff_member_required
@permission_required('operations.change_classification', raise_exception=True)
def reception_report_change_status(request, pk):
    """Changer le statut d'un rapport de réception"""
    classification = get_object_or_404(Classification, pk=pk)

    if request.method == 'POST':
        new_status = request.POST.get('status')

        # Vérifier que le nouveau statut est valide
        valid_statuses = [choice[0] for choice in Classification.STATUS_CHOICES]
        if new_status not in valid_statuses:
            messages.error(request, 'Statut invalide!')
            return redirect('portal_admin:reception_report_detail', pk=pk)

        # Vérifier les règles de changement de statut
        if classification.status == 'validated':
            # Une fois validé, on ne peut plus changer le statut
            messages.error(request, 'Un rapport validé ne peut plus être modifié.')
            return redirect('portal_admin:reception_report_detail', pk=pk)

        # Appliquer le changement
        old_status = classification.get_status_display()
        classification.status = new_status
        classification.save()

        new_status_display = classification.get_status_display()
        messages.success(request, f'Statut du rapport changé de "{old_status}" à "{new_status_display}"')
        return redirect('portal_admin:reception_report_detail', pk=pk)

    return redirect('portal_admin:reception_report_detail', pk=pk)


