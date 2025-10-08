# -*- coding: utf-8 -*-
from django.shortcuts import redirect
from django.urls import resolve
from django.contrib import messages


class RolePermissionMiddleware:
    """
    Middleware pour gérer les permissions des utilisateurs.
    - Contrôle l'accès aux URLs en fonction des permissions
    - Ajoute des attributs utiles à l'objet User pour faciliter les vérifications
    """
    def __init__(self, get_response):
        self.get_response = get_response

        # Mapping des URL patterns vers les permissions requises
        # Format: 'nom_url': 'permission_codename'
        self.url_permissions = {
            # Administration (authentication app)
            'users_list': 'authentication.view_user',
            'user_create': 'authentication.add_user',
            'user_detail': 'authentication.view_user',
            'user_update': 'authentication.change_user',
            'toggle_user_status': 'authentication.change_user',
            'admin_reset_password': 'authentication.change_user',
            'roles_list': 'authentication.view_role',
            'role_create': 'authentication.add_role',
            'role_detail': 'authentication.view_role',
            'role_update': 'authentication.change_role',
            'role_delete': 'authentication.delete_role',
            'role_permissions': 'authentication.change_role',
            'user_action_logs': 'authentication.view_useractionlog',
            'debug_role_permissions': 'authentication.view_role',
        }

    def __call__(self, request):
        # Traiter la requête avant la vue
        if request.user.is_authenticated:
            # Résoudre l'URL pour obtenir le nom de la vue
            resolved = resolve(request.path)
            url_name = resolved.url_name

            # Vérifier si cette URL nécessite une permission
            if url_name in self.url_permissions:
                required_permission = self.url_permissions[url_name]

                # Vérifier si l'utilisateur a la permission
                if not request.user.has_perm(required_permission):
                    messages.error(request, "Vous n'avez pas les permissions nécessaires pour accéder à cette page.")
                    return redirect('portal_admin:index')  # Rediriger vers la page d'accueil du portal

        response = self.get_response(request)
        return response
