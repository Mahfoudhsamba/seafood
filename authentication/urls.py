from django.urls import path
from . import views

urlpatterns = [
    # URLs pour la gestion des utilisateurs
    path('users/', views.users_list, name='users_list'),
    path('users/create/', views.user_create, name='user_create'),
    path('users/<int:user_id>/', views.user_detail, name='user_detail'),
    path('users/<int:user_id>/update/', views.user_update, name='user_update'),
    path('users/<int:user_id>/toggle-status/', views.toggle_user_status, name='toggle_user_status'),
    path('users/<int:user_id>/reset-password/', views.admin_reset_password, name='admin_reset_password'),

    # URLs pour la gestion des rôles
    path('roles/', views.roles_list, name='roles_list'),
    path('roles/create/', views.role_create, name='role_create'),
    path('roles/<int:role_id>/', views.role_detail, name='role_detail'),
    path('roles/<int:role_id>/update/', views.role_update, name='role_update'),
    path('roles/<int:role_id>/delete/', views.role_delete, name='role_delete'),
    path('roles/<int:role_id>/permissions/', views.role_permissions, name='role_permissions'),

    # URLs pour les logs
    path('logs/', views.user_action_logs, name='user_action_logs'),

    # URL de debug
    path('debug/permissions/', views.debug_role_permissions, name='debug_role_permissions'),
]
