from django.db import models
from django.conf import settings
from django.core.validators import RegexValidator
from django.db.models.signals import post_save, pre_save, pre_delete
from django.dispatch import receiver
import os

# Create your models here.

class UserProfile(models.Model):
    """
    Modèle pour le profil utilisateur étendu
    """
    LANGUAGE_CHOICES = [
        ('fr', 'Français'),
        ('ar', 'العربية'),
        ('en', 'English'),
    ]

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile', verbose_name='Utilisateur')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name='Avatar')
    phone = models.CharField(max_length=20, blank=True, verbose_name='Téléphone')
    address = models.TextField(blank=True, verbose_name='Adresse')
    language = models.CharField(max_length=2, choices=LANGUAGE_CHOICES, default='fr', verbose_name='Langue')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Date de création')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Date de modification')

    class Meta:
        verbose_name = 'Profil utilisateur'
        verbose_name_plural = 'Profils utilisateurs'

    def __str__(self):
        return f"Profil de {self.user.username}"


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    """Créer automatiquement un profil lors de la création d'un utilisateur"""
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def save_user_profile(sender, instance, **kwargs):
    """Sauvegarder le profil lors de la sauvegarde de l'utilisateur"""
    if hasattr(instance, 'profile'):
        instance.profile.save()


def client_logo_path(instance, filename):
    """Génère le chemin du logo client avec nomenclature"""
    ext = filename.split('.')[-1].lower()
    if instance.pk:
        return f'clients/client_{instance.pk}.{ext}'
    return f'clients/{filename}'


class Client(models.Model):
    """
    Modèle pour la gestion des clients
    """
    CLIENT_TYPE_CHOICES = [
        ('individual', 'Particulier'),
        ('company', 'Entreprise'),
        ('organization', 'Organisation'),
    ]

    STATUS_CHOICES = [
        ('active', 'Actif'),
        ('inactive', 'Inactif'),
        ('suspended', 'Suspendu'),
    ]

    # Code comptable unique
    accounting_code = models.CharField(
        max_length=8,
        unique=True,
        verbose_name='Code Comptable',
        help_text='Format: 41XXXXXX (généré automatiquement)'
    )

    # Informations de base
    name = models.CharField(max_length=200, verbose_name='Nom du client')
    client_type = models.CharField(
        max_length=20,
        choices=CLIENT_TYPE_CHOICES,
        default='individual',
        verbose_name='Type de client'
    )
    website = models.URLField(blank=True, null=True, verbose_name='Site web')
    responsible = models.CharField(max_length=200, blank=True, verbose_name='Responsable')

    # Coordonnées
    mobile_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Le numéro de portable doit être au format: '+999999999'. Jusqu'à 15 chiffres autorisés."
    )
    mobile = models.CharField(
        validators=[mobile_regex],
        max_length=17,
        blank=True,
        verbose_name='Portable'
    )

    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Le numéro de téléphone doit être au format: '+999999999'. Jusqu'à 15 chiffres autorisés."
    )
    phone = models.CharField(
        validators=[phone_regex],
        max_length=17,
        blank=True,
        verbose_name='Téléphone'
    )

    email = models.EmailField(blank=True, verbose_name='Email')

    # Adresse
    address = models.TextField(blank=True, verbose_name='Adresse')
    city = models.CharField(max_length=100, blank=True, verbose_name='Ville')
    postal_code = models.CharField(max_length=20, blank=True, verbose_name='Code postal')
    country = models.CharField(max_length=100, default='Mauritanie', verbose_name='Pays')

    # Informations légales
    trade_register = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='Numéro de registre de commerce'
    )
    tax_id = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='Numéro d\'identification fiscal'
    )

    # Statut et observations
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active',
        verbose_name='Statut'
    )
    observations = models.TextField(
        blank=True,
        verbose_name='Observations',
        help_text='Informations supplémentaires sur le client'
    )

    # Logo
    logo = models.ImageField(
        upload_to=client_logo_path,
        blank=True,
        null=True,
        verbose_name='Logo'
    )

    # Dates
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Date de création')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Date de modification')

    class Meta:
        verbose_name = 'Client'
        verbose_name_plural = 'Clients'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['accounting_code']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.accounting_code} - {self.name}"

    def save(self, *args, **kwargs):
        # Générer le code comptable s'il n'existe pas
        if not self.accounting_code:
            self.accounting_code = self.generate_accounting_code()
        super().save(*args, **kwargs)

    @staticmethod
    def generate_accounting_code():
        """Génère un code comptable unique au format 41XXXXXX"""
        last_client = Client.objects.order_by('-accounting_code').first()
        if last_client and last_client.accounting_code:
            # Extraire le numéro et l'incrémenter
            last_number = int(last_client.accounting_code[2:])
            new_number = last_number + 1
        else:
            # Premier client
            new_number = 1

        # Formater avec 6 chiffres
        return f"41{new_number:06d}"


@receiver(pre_save, sender=Client)
def delete_old_client_logo_on_update(sender, instance, **kwargs):
    """Supprime l'ancien logo lors de la modification"""
    if not instance.pk:
        return False

    try:
        old_instance = Client.objects.get(pk=instance.pk)
    except Client.DoesNotExist:
        return False

    if old_instance.logo and instance.logo and old_instance.logo != instance.logo:
        if os.path.isfile(old_instance.logo.path):
            os.remove(old_instance.logo.path)


@receiver(pre_delete, sender=Client)
def delete_client_logo_on_delete(sender, instance, **kwargs):
    """Supprime le logo lors de la suppression de l'objet Client"""
    if instance.logo:
        if os.path.isfile(instance.logo.path):
            os.remove(instance.logo.path)


def supplier_logo_path(instance, filename):
    """Génère le chemin du logo fournisseur avec nomenclature"""
    ext = filename.split('.')[-1].lower()
    if instance.pk:
        return f'suppliers/supplier_{instance.pk}.{ext}'
    return f'suppliers/{filename}'


class Supplier(models.Model):
    """
    Modèle pour la gestion des fournisseurs
    """
    CATEGORY_CHOICES = [
        ('logistics', 'Logistiques'),
        ('manufacturing', 'Fabrication'),
        ('mining', 'Exploitation minière'),
        ('construction', 'Fabrication'),
        ('administration', 'Administration'),
        ('fish_food', 'Pêche & alimentation'),
        ('other', 'Autre'),
    ]

    STATUS_CHOICES = [
        ('active', 'Actif'),
        ('suspended', 'Suspendu'),
    ]

    # Code comptable unique
    accounting_code = models.CharField(
        max_length=8,
        unique=True,
        verbose_name='Compte Comptable',
        help_text='Format: 40XXXXXX (généré automatiquement)'
    )

    # Informations de base
    name = models.CharField(max_length=200, verbose_name='Nom du fournisseur')
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        verbose_name='Catégorie (Secteur d\'activité)'
    )

    # Informations légales
    tax_id = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='Numéro d\'identification fiscale'
    )
    trade_register = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='Numéro de registre de commerce'
    )

    # Termes de paiement
    payment_terms = models.PositiveIntegerField(
        default=30,
        verbose_name='Termes de paiement (jours)',
        help_text='Nombre de jours pour le paiement'
    )

    # Coordonnées
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Le numéro de téléphone doit être au format: '+999999999'. Jusqu'à 15 chiffres autorisés."
    )
    contact_phone = models.CharField(
        validators=[phone_regex],
        max_length=17,
        blank=True,
        verbose_name='Téléphone de contact'
    )

    mobile_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Le numéro de portable doit être au format: '+999999999'. Jusqu'à 15 chiffres autorisés."
    )
    mobile = models.CharField(
        validators=[mobile_regex],
        max_length=17,
        blank=True,
        verbose_name='Téléphone mobile'
    )

    email = models.EmailField(blank=True, verbose_name='Email')
    website = models.URLField(blank=True, null=True, verbose_name='Site web')

    # Adresse
    address = models.TextField(blank=True, verbose_name='Adresse')
    city = models.CharField(max_length=100, blank=True, verbose_name='Ville')
    country = models.CharField(max_length=100, default='Mauritanie', verbose_name='Pays')

    # Statut
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active',
        verbose_name='Statut'
    )

    # Logo
    logo = models.ImageField(
        upload_to=supplier_logo_path,
        blank=True,
        null=True,
        verbose_name='Logo'
    )

    # Dates
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Date de création')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Date de modification')

    class Meta:
        verbose_name = 'Fournisseur'
        verbose_name_plural = 'Fournisseurs'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['accounting_code']),
            models.Index(fields=['status']),
            models.Index(fields=['category']),
        ]

    def __str__(self):
        return f"{self.accounting_code} - {self.name}"

    def save(self, *args, **kwargs):
        # Générer le code comptable s'il n'existe pas
        if not self.accounting_code:
            self.accounting_code = self.generate_accounting_code()
        super().save(*args, **kwargs)

    @staticmethod
    def generate_accounting_code():
        """Génère un code comptable unique au format 40XXXXXX"""
        last_supplier = Supplier.objects.order_by('-accounting_code').first()
        if last_supplier and last_supplier.accounting_code:
            # Extraire le numéro et l'incrémenter
            last_number = int(last_supplier.accounting_code[2:])
            new_number = last_number + 1
        else:
            # Premier fournisseur
            new_number = 1

        # Formater avec 6 chiffres
        return f"40{new_number:06d}"


@receiver(pre_save, sender=Supplier)
def delete_old_supplier_logo_on_update(sender, instance, **kwargs):
    """Supprime l'ancien logo lors de la modification"""
    if not instance.pk:
        return False

    try:
        old_instance = Supplier.objects.get(pk=instance.pk)
    except Supplier.DoesNotExist:
        return False

    if old_instance.logo and instance.logo and old_instance.logo != instance.logo:
        if os.path.isfile(old_instance.logo.path):
            os.remove(old_instance.logo.path)


@receiver(pre_delete, sender=Supplier)
def delete_supplier_logo_on_delete(sender, instance, **kwargs):
    """Supprime le logo lors de la suppression de l'objet Supplier"""
    if instance.logo:
        if os.path.isfile(instance.logo.path):
            os.remove(instance.logo.path)
