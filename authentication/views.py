from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from .models import User, Role, UserActionLog
from .forms import UserCreateForm, UserUpdateForm, AdminPasswordResetForm, RoleForm, RolePermissionsForm
from .utils import log_user_action


# ============================================
# VUES POUR LA GESTION DES UTILISATEURS
# ============================================

@login_required
@permission_required('authentication.view_user', raise_exception=True)
def users_list(request):
    """Liste tous les utilisateurs avec recherche et pagination"""
    query = request.GET.get('q', '')
    role_filter = request.GET.get('role', '')
    status_filter = request.GET.get('status', '')

    users = User.objects.select_related('role').all()

    # Filtres de recherche
    if query:
        users = users.filter(
            Q(username__icontains=query) |
            Q(email__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query)
        )

    if role_filter:
        users = users.filter(role_id=role_filter)

    if status_filter == 'active':
        users = users.filter(is_active=True)
    elif status_filter == 'inactive':
        users = users.filter(is_active=False)

    # Pagination
    paginator = Paginator(users, 15)
    page_number = request.GET.get('page')
    users_page = paginator.get_page(page_number)

    roles = Role.objects.all()

    context = {
        'users': users_page,
        'roles': roles,
        'query': query,
        'role_filter': role_filter,
        'status_filter': status_filter,
    }

    return render(request, 'authentication/users_list.html', context)


@login_required
@permission_required('authentication.add_user', raise_exception=True)
def user_create(request):
    """Créer un nouvel utilisateur"""
    if request.method == 'POST':
        form = UserCreateForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_staff = True  # Donner l'accès au portail par défaut
            user.save()
            form.save_m2m()  # Sauvegarder les relations many-to-many (comme le rôle)
            log_user_action(
                user=request.user,
                action='create',
                target_model='User',
                target_id=user.id,
                details=f"Création de l'utilisateur {user.username}",
                request=request
            )
            messages.success(request, f"L'utilisateur {user.username} a été créé avec succès.")
            return redirect('authentication:user_detail', user_id=user.id)
    else:
        form = UserCreateForm()

    context = {'form': form}
    return render(request, 'authentication/user_create.html', context)


@login_required
@permission_required('authentication.view_user', raise_exception=True)
def user_detail(request, user_id):
    """Afficher les détails d'un utilisateur"""
    user_obj = get_object_or_404(User.objects.select_related('role'), id=user_id)

    # Récupérer les dernières actions de l'utilisateur
    recent_actions = user_obj.action_logs.all()[:10]

    context = {
        'user': user_obj,
        'recent_actions': recent_actions,
    }

    return render(request, 'authentication/user_detail.html', context)


@login_required
@permission_required('authentication.change_user', raise_exception=True)
def user_update(request, user_id):
    """Mettre à jour un utilisateur"""
    import os
    from django.core.files.base import ContentFile

    user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        # Vérifier si un nouveau fichier avatar a été uploadé
        has_new_avatar = 'avatar' in request.FILES

        # Récupérer l'ancien avatar avant toute modification
        old_avatar_path = None
        if has_new_avatar:
            try:
                old_instance = User.objects.get(pk=user.id)
                if old_instance.avatar:
                    old_avatar_path = old_instance.avatar.path
            except User.DoesNotExist:
                pass

        form = UserUpdateForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            # Sauvegarder sans commit pour pouvoir modifier l'avatar
            user = form.save(commit=False)

            # Gérer le renommage de l'avatar si un nouveau fichier a été uploadé
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

            log_user_action(
                user=request.user,
                action='update',
                target_model='User',
                target_id=user.id,
                details=f"Mise à jour de l'utilisateur {user.username}",
                request=request
            )
            messages.success(request, f"L'utilisateur {user.username} a été mis à jour avec succès.")
            return redirect('authentication:user_detail', user_id=user.id)
    else:
        form = UserUpdateForm(instance=user)

    context = {
        'form': form,
        'user_obj': user,
    }

    return render(request, 'authentication/user_update.html', context)


@login_required
@permission_required('authentication.change_user', raise_exception=True)
def toggle_user_status(request, user_id):
    """Activer/Désactiver un utilisateur"""
    user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        user.is_active = not user.is_active
        user.save()

        status = "activé" if user.is_active else "désactivé"
        log_user_action(
            user=request.user,
            action='status_change',
            target_model='User',
            target_id=user.id,
            details=f"Utilisateur {user.username} {status}",
            request=request
        )

        messages.success(request, f"L'utilisateur {user.username} a été {status}.")

    return redirect('authentication:user_detail', user_id=user.id)


@login_required
@permission_required('authentication.change_user', raise_exception=True)
def admin_reset_password(request, user_id):
    """Réinitialiser le mot de passe d'un utilisateur (admin)"""
    user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        form = AdminPasswordResetForm(request.POST)
        if form.is_valid():
            new_password = form.cleaned_data['new_password1']
            user.set_password(new_password)
            user.save()

            log_user_action(
                user=request.user,
                action='password_change',
                target_model='User',
                target_id=user.id,
                details=f"Réinitialisation du mot de passe pour {user.username}",
                request=request
            )

            messages.success(request, f"Le mot de passe de {user.username} a été réinitialisé.")
            return redirect('authentication:user_detail', user_id=user.id)
    else:
        form = AdminPasswordResetForm()

    context = {
        'form': form,
        'user_obj': user,
    }

    return render(request, 'authentication/admin_reset_password.html', context)


# ============================================
# VUES POUR LA GESTION DES RÔLES
# ============================================

@login_required
@permission_required('authentication.view_role', raise_exception=True)
def roles_list(request):
    """Liste tous les rôles"""
    query = request.GET.get('q', '')

    roles = Role.objects.prefetch_related('permissions').all()

    if query:
        roles = roles.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query)
        )

    # Ajouter le nombre d'utilisateurs pour chaque rôle
    for role in roles:
        role.users_count = role.users.count()

    context = {
        'roles': roles,
        'query': query,
    }

    return render(request, 'authentication/roles_list.html', context)


@login_required
@permission_required('authentication.add_role', raise_exception=True)
def role_create(request):
    """Créer un nouveau rôle"""
    if request.method == 'POST':
        form = RoleForm(request.POST)
        if form.is_valid():
            role = form.save()
            log_user_action(
                user=request.user,
                action='create',
                target_model='Role',
                target_id=role.id,
                details=f"Création du rôle {role.name}",
                request=request
            )
            messages.success(request, f"Le rôle {role.name} a été créé avec succès.")
            return redirect('authentication:role_detail', role_id=role.id)
    else:
        form = RoleForm()

    context = {'form': form}
    return render(request, 'authentication/role_create.html', context)


@login_required
@permission_required('authentication.view_role', raise_exception=True)
def role_detail(request, role_id):
    """Afficher les détails d'un rôle"""
    role = get_object_or_404(Role.objects.prefetch_related('permissions', 'users'), id=role_id)

    # Grouper les permissions par application
    permissions_by_app = {}
    for perm in role.permissions.select_related('content_type').all():
        app_label = perm.content_type.app_label
        if app_label not in permissions_by_app:
            permissions_by_app[app_label] = []
        permissions_by_app[app_label].append(perm)

    # Calculer les statistiques
    all_users = role.users.all()
    users_count = all_users.count()
    active_users_count = all_users.filter(is_active=True).count()

    context = {
        'role': role,
        'permissions_by_app': permissions_by_app,
        'users': all_users[:10],  # Limiter à 10 utilisateurs pour l'affichage
        'users_count': users_count,
        'active_users_count': active_users_count,
    }

    return render(request, 'authentication/role_detail.html', context)


@login_required
@permission_required('authentication.change_role', raise_exception=True)
def role_update(request, role_id):
    """Mettre à jour un rôle"""
    role = get_object_or_404(Role, id=role_id)

    if request.method == 'POST':
        form = RoleForm(request.POST, instance=role)
        if form.is_valid():
            role = form.save()
            log_user_action(
                user=request.user,
                action='update',
                target_model='Role',
                target_id=role.id,
                details=f"Mise à jour du rôle {role.name}",
                request=request
            )
            messages.success(request, f"Le rôle {role.name} a été mis à jour avec succès.")
            return redirect('authentication:role_detail', role_id=role.id)
    else:
        form = RoleForm(instance=role)

    context = {
        'form': form,
        'role': role,
    }

    return render(request, 'authentication/role_update.html', context)


@login_required
@permission_required('authentication.delete_role', raise_exception=True)
def role_delete(request, role_id):
    """Supprimer un rôle"""
    role = get_object_or_404(Role, id=role_id)

    if request.method == 'POST':
        role_name = role.name
        role.delete()
        log_user_action(
            user=request.user,
            action='delete',
            target_model='Role',
            target_id=role_id,
            details=f"Suppression du rôle {role_name}",
            request=request
        )
        messages.success(request, f"Le rôle {role_name} a été supprimé.")
        return redirect('authentication:roles_list')

    context = {'role': role}
    return render(request, 'authentication/role_confirm_delete.html', context)


@login_required
@permission_required('authentication.change_role', raise_exception=True)
def role_permissions(request, role_id):
    """Gérer les permissions d'un rôle"""
    role = get_object_or_404(Role, id=role_id)

    if request.method == 'POST':
        form = RolePermissionsForm(request.POST, role=role)
        if form.is_valid():
            permissions = form.cleaned_data['permissions']
            role.permissions.set(permissions)

            log_user_action(
                user=request.user,
                action='permission_change',
                target_model='Role',
                target_id=role.id,
                details=f"Mise à jour des permissions du rôle {role.name}",
                request=request
            )

            messages.success(request, f"Les permissions du rôle {role.name} ont été mises à jour.")
            return redirect('authentication:role_detail', role_id=role.id)
    else:
        form = RolePermissionsForm(role=role)

    permissions_by_app = form.get_permissions_by_app()

    context = {
        'form': form,
        'role': role,
        'permissions_by_app': permissions_by_app,
    }

    return render(request, 'authentication/role_permissions.html', context)


# ============================================
# VUES POUR LES LOGS D'ACTIONS
# ============================================

@login_required
@permission_required('authentication.view_useractionlog', raise_exception=True)
def user_action_logs(request):
    """Afficher les logs d'actions des utilisateurs"""
    query = request.GET.get('q', '')
    action_filter = request.GET.get('action', '')
    user_filter = request.GET.get('user', '')

    logs = UserActionLog.objects.select_related('user').all()

    if query:
        logs = logs.filter(
            Q(details__icontains=query) |
            Q(user__username__icontains=query)
        )

    if action_filter:
        logs = logs.filter(action=action_filter)

    if user_filter:
        logs = logs.filter(user_id=user_filter)

    # Pagination
    paginator = Paginator(logs, 50)
    page_number = request.GET.get('page')
    logs_page = paginator.get_page(page_number)

    # Pour le filtre par utilisateur
    users = User.objects.all().order_by('username')

    context = {
        'logs': logs_page,
        'query': query,
        'action_filter': action_filter,
        'user_filter': user_filter,
        'action_choices': UserActionLog.ACTION_CHOICES,
        'users': users,
    }

    return render(request, 'authentication/user_action_logs.html', context)


# ============================================
# VUE DE DEBUG (à supprimer en production)
# ============================================

@login_required
@permission_required('authentication.view_role', raise_exception=True)
def debug_role_permissions(request):
    """Vue de debug pour afficher toutes les permissions disponibles"""
    from django.contrib.auth.models import Permission
    from django.contrib.contenttypes.models import ContentType

    permissions_by_app = {}
    permissions = Permission.objects.select_related('content_type').all().order_by('content_type__app_label', 'codename')

    for perm in permissions:
        app_label = perm.content_type.app_label
        if app_label not in permissions_by_app:
            permissions_by_app[app_label] = []
        permissions_by_app[app_label].append({
            'id': perm.id,
            'codename': perm.codename,
            'name': perm.name,
            'full_codename': f"{app_label}.{perm.codename}"
        })

    context = {
        'permissions_by_app': permissions_by_app,
    }

    return render(request, 'authentication/debug_permissions.html', context)
