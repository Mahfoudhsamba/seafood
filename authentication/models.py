from django.db import models
from django.contrib.auth.models import AbstractUser, Permission
from django.db.models.signals import pre_save, post_delete
from django.dispatch import receiver
import os
from django.utils.text import slugify
from django.core.files.base import ContentFile


def user_avatar_path(instance, filename):
    """Génère le chemin de sauvegarde de l'avatar - fonction simple qui retourne juste le chemin"""
    # Cette fonction est appelée par Django mais on gère le renommage manuellement dans la vue
    return os.path.join('avatars', filename)


class Role(models.Model):
    """Modèle pour gérer les rôles personnalisés"""
    name = models.CharField(max_length=100, unique=True, verbose_name="Nom du rôle")
    description = models.TextField(blank=True, verbose_name="Description")
    permissions = models.ManyToManyField(
        Permission,
        blank=True,
        verbose_name="Permissions",
        related_name='roles'
    )
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Date de modification")

    class Meta:
        verbose_name = "Rôle"
        verbose_name_plural = "Rôles"
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_permissions_list(self):
        """Retourne la liste des permissions du rôle"""
        return list(self.permissions.values_list('codename', flat=True))


class User(AbstractUser):
    """Modèle utilisateur personnalisé avec support des rôles"""
    email = models.EmailField(max_length=191, unique=True, verbose_name="Email")
    phone = models.CharField(max_length=20, blank=True, verbose_name="Téléphone")
    avatar = models.ImageField(upload_to=user_avatar_path, blank=True, null=True, verbose_name="Avatar")
    role = models.ForeignKey(
        Role,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='users',
        verbose_name="Rôle"
    )
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Date de modification")

    class Meta:
        verbose_name = "Utilisateur"
        verbose_name_plural = "Utilisateurs"
        ordering = ['-created_at']

    def __str__(self):
        return self.username

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def get_role_permissions(self):
        """Retourne les permissions du rôle de l'utilisateur"""
        if self.role:
            return self.role.permissions.all()
        return Permission.objects.none()

    def has_perm(self, perm, obj=None):
        """Vérifie si l'utilisateur a une permission spécifique"""
        # Les superusers ont toutes les permissions
        if self.is_active and self.is_superuser:
            return True

        # Vérifier les permissions du rôle
        if self.role and self.is_active:
            # perm est au format 'app_label.codename' (ex: 'authentication.view_user')
            try:
                app_label, codename = perm.split('.')
                # Vérifier si cette permission existe dans le rôle
                if self.role.permissions.filter(
                    content_type__app_label=app_label,
                    codename=codename
                ).exists():
                    return True
            except ValueError:
                # Si le format de perm n'est pas valide, passer à la vérification par défaut
                pass

        # Vérifier les permissions directes de l'utilisateur
        return super().has_perm(perm, obj)

    def has_module_perms(self, app_label):
        """Vérifie si l'utilisateur a des permissions pour un module"""
        if self.is_active and self.is_superuser:
            return True

        if self.role:
            role_perms = self.role.permissions.filter(
                content_type__app_label=app_label
            )
            if role_perms.exists():
                return True

        return super().has_module_perms(app_label)


class UserActionLog(models.Model):
    """Modèle pour logger les actions des utilisateurs"""
    ACTION_CHOICES = [
        ('create', 'Création'),
        ('update', 'Mise à jour'),
        ('delete', 'Suppression'),
        ('login', 'Connexion'),
        ('logout', 'Déconnexion'),
        ('password_change', 'Changement de mot de passe'),
        ('status_change', 'Changement de statut'),
        ('permission_change', 'Changement de permissions'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='action_logs',
        verbose_name="Utilisateur"
    )
    action = models.CharField(max_length=50, choices=ACTION_CHOICES, verbose_name="Action")
    target_model = models.CharField(max_length=100, blank=True, verbose_name="Modèle cible")
    target_id = models.IntegerField(null=True, blank=True, verbose_name="ID de la cible")
    details = models.TextField(blank=True, verbose_name="Détails")
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name="Adresse IP")
    user_agent = models.TextField(blank=True, verbose_name="User Agent")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date")

    class Meta:
        verbose_name = "Log d'action utilisateur"
        verbose_name_plural = "Logs d'actions utilisateurs"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user} - {self.action} - {self.created_at}"


# ============================================
# SIGNAL POUR LA SUPPRESSION DES AVATARS
# ============================================

@receiver(post_delete, sender=User)
def delete_avatar_on_user_delete(sender, instance, **kwargs):
    """Supprimer l'avatar quand l'utilisateur est supprimé"""
    if instance.avatar:
        try:
            if os.path.isfile(instance.avatar.path):
                os.remove(instance.avatar.path)
        except Exception:
            pass
