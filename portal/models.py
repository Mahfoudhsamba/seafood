from django.db import models
from django.utils.text import slugify
from django.core.validators import MinValueValidator
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

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

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile', verbose_name='Utilisateur')
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


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Créer automatiquement un profil lors de la création d'un utilisateur"""
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Sauvegarder le profil lors de la sauvegarde de l'utilisateur"""
    if hasattr(instance, 'profile'):
        instance.profile.save()

class Gallery(models.Model):
    """
    Modèle pour la galerie d'images
    """
    image = models.ImageField(upload_to='gallery/', verbose_name='Image')
    title = models.CharField(max_length=200, verbose_name='Titre')
    description = models.TextField(verbose_name='Description')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Date de création')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Date de modification')
    is_active = models.BooleanField(default=True, verbose_name='Actif')
    order = models.IntegerField(default=0, verbose_name='Ordre d\'affichage')

    class Meta:
        verbose_name = 'Image de galerie'
        verbose_name_plural = 'Galerie'
        ordering = ['order', '-created_at']

    def __str__(self):
        return self.title


class Product(models.Model):
    """
    Modèle pour les produits de la mer
    """
    CATEGORY_CHOICES = [
        ('cephalopods', 'Céphalopodes'),
        ('fillets', 'Filets & Découpes'),
        ('fresh', 'Poissons Frais'),
        ('frozen', 'Poissons Congelés'),
        ('crustaceans', 'Crustacés'),
    ]

    product = models.CharField(max_length=200, verbose_name='Nom du produit')
    slug = models.SlugField(max_length=250, unique=True, blank=True, verbose_name='Slug')
    local_name = models.CharField(max_length=200, blank=True, verbose_name='Nom local')
    scientific_name = models.CharField(max_length=200, blank=True, verbose_name='Nom scientifique')
    image = models.ImageField(upload_to='products/', verbose_name='Image')
    weight = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
        help_text='Poids estimé par unité (en kg)',
        verbose_name='Poids (kg)'
    )
    description = models.TextField(verbose_name='Description')
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
        help_text='Prix par kilogramme',
        verbose_name='Prix /kg'
    )
    category = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES,
        verbose_name='Catégorie'
    )

    # Champs additionnels
    is_available = models.BooleanField(default=True, verbose_name='Disponible')
    is_featured = models.BooleanField(default=False, verbose_name='Produit vedette')
    stock_quantity = models.IntegerField(default=0, verbose_name='Quantité en stock (kg)')
    minimum_order = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=1.00,
        validators=[MinValueValidator(0.01)],
        help_text='Quantité minimale de commande (en kg)',
        verbose_name='Commande minimale (kg)'
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Date de création')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Date de modification')

    class Meta:
        verbose_name = 'Produit'
        verbose_name_plural = 'Produits'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['is_available']),
        ]

    def __str__(self):
        return self.product

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.product)
        super().save(*args, **kwargs)

    def get_total_price(self):
        """Calcule le prix total basé sur le poids"""
        return self.weight * self.price

    def is_in_stock(self):
        """Vérifie si le produit est en stock"""
        return self.stock_quantity > 0


class Service(models.Model):
    """
    Modèle pour les services offerts par PPA
    """
    name = models.CharField(max_length=200, verbose_name='Nom du service')
    slug = models.SlugField(max_length=250, unique=True, blank=True, verbose_name='Slug')
    description = models.TextField(verbose_name='Description')
    image = models.ImageField(upload_to='services/', verbose_name='Image', blank=True, null=True)
    is_active = models.BooleanField(default=True, verbose_name='Actif')
    order = models.IntegerField(default=0, verbose_name='Ordre d\'affichage')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Date de création')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Date de modification')

    class Meta:
        verbose_name = 'Service'
        verbose_name_plural = 'Services'
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class FAQ(models.Model):
    """
    Modèle pour les questions fréquemment posées concernant les services
    """
    question = models.CharField(max_length=500, verbose_name='Question')
    answer = models.TextField(verbose_name='Réponse')
    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name='faqs',
        verbose_name='Service concerné',
        null=True,
        blank=True
    )
    order = models.IntegerField(default=0, verbose_name='Ordre d\'affichage')
    is_active = models.BooleanField(default=True, verbose_name='Actif')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Date de création')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Date de modification')

    class Meta:
        verbose_name = 'FAQ'
        verbose_name_plural = 'FAQs'
        ordering = ['order', '-created_at']

    def __str__(self):
        return self.question
