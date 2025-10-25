from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MinLengthValidator, MaxLengthValidator
from django.core.exceptions import ValidationError
from decimal import Decimal

# Create your models here.


class ServiceCategory(models.Model):
    """
    Modèle pour les catégories de services
    """
    STATUS_CHOICES = [
        ('active', 'Actif'),
        ('suspended', 'Suspendu'),
    ]

    # Avatar/Image
    avatar = models.ImageField(
        upload_to='service_categories/',
        blank=True,
        null=True,
        verbose_name='Avatar'
    )

    # Nom de la catégorie
    name = models.CharField(
        max_length=200,
        unique=True,
        verbose_name='Nom de la catégorie'
    )

    # Description
    description = models.TextField(
        blank=True,
        verbose_name='Description'
    )

    # Statut
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active',
        verbose_name='État'
    )

    # Métadonnées
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Date de création'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Date de modification'
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_service_categories',
        verbose_name='Créé par'
    )

    class Meta:
        verbose_name = 'Catégorie de service'
        verbose_name_plural = 'Catégories de services'
        ordering = ['name']

    def __str__(self):
        return self.name

    @property
    def is_active(self):
        """Vérifie si la catégorie est active"""
        return self.status == 'active'


class Service(models.Model):
    """
    Modèle pour les services offerts par l'entreprise
    """
    STATUS_CHOICES = [
        ('active', 'Actif'),
        ('suspended', 'Suspendu'),
    ]

    # Code unique sur 4 chiffres (1000-9999)
    code = models.CharField(
        max_length=4,
        unique=True,
        validators=[
            MinLengthValidator(4),
            MaxLengthValidator(4),
        ],
        verbose_name='Code du service',
        help_text='Code unique sur 4 chiffres (1000-9999). Codes 1000-1010 réservés au système.'
    )

    # Nom du service
    name = models.CharField(
        max_length=200,
        verbose_name='Nom du service'
    )

    # État du service
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active',
        verbose_name='État'
    )

    # Description
    description = models.TextField(
        blank=True,
        verbose_name='Description du service'
    )

    # Montant du service (peut être 0)
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        default=Decimal('0.00'),
        verbose_name='Montant',
        help_text='Montant du service (peut être 0)'
    )

    # Catégorie
    category = models.ForeignKey(
        ServiceCategory,
        on_delete=models.PROTECT,
        related_name='services',
        verbose_name='Catégorie'
    )

    # Métadonnées
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Date de création'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Date de modification'
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_services',
        verbose_name='Créé par'
    )

    class Meta:
        verbose_name = 'Service'
        verbose_name_plural = 'Services'
        ordering = ['code']
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['status']),
            models.Index(fields=['category']),
        ]

    def __str__(self):
        return f"{self.code} - {self.name}"

    def clean(self):
        """Validation personnalisée"""
        super().clean()

        # Vérifier que le code est composé uniquement de chiffres
        if not self.code.isdigit():
            raise ValidationError({'code': 'Le code doit être composé uniquement de chiffres.'})

        code_int = int(self.code)

        # Vérifier que le code est entre 1000 et 9999
        if code_int < 1000 or code_int > 9999:
            raise ValidationError({'code': 'Le code doit être entre 1000 et 9999.'})

        # Note: Les codes 1001-1010 sont réservés mais l'utilisateur peut les utiliser
        # pour définir ses propres services système. Pas de restriction ici.

    def save(self, *args, **kwargs):
        # Si le code est "auto", générer un code automatiquement
        if self.code == "auto" or not self.code:
            self.code = self.generate_code()

        # Valider avant de sauvegarder
        self.full_clean()
        super().save(*args, **kwargs)

    @staticmethod
    def generate_code():
        """Génère un code unique commençant par 1011"""
        # Chercher le dernier service avec un code >= 1011
        last_service = Service.objects.filter(
            code__gte='1011'
        ).order_by('-code').first()

        if last_service:
            try:
                last_code = int(last_service.code)
                new_code = last_code + 1
            except ValueError:
                new_code = 1011
        else:
            new_code = 1011

        # Vérifier que le code n'existe pas déjà (au cas où)
        while Service.objects.filter(code=str(new_code)).exists():
            new_code += 1

        # Vérifier qu'on ne dépasse pas 9999
        if new_code > 9999:
            raise ValidationError('Tous les codes disponibles ont été utilisés.')

        return str(new_code)

    @property
    def is_active(self):
        """Vérifie si le service est actif"""
        return self.status == 'active'

    @property
    def is_system_reserved(self):
        """Vérifie si c'est un code réservé au système"""
        try:
            code_int = int(self.code)
            return 1000 <= code_int <= 1010
        except ValueError:
            return False


class FishCategory(models.Model):
    """
    Modèle pour les catégories de poissons
    """
    name = models.CharField(max_length=200, unique=True, verbose_name='Nom de la catégorie')
    description = models.TextField(blank=True, verbose_name='Description')
    is_active = models.BooleanField(default=True, verbose_name='Actif')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Date de création')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Date de modification')

    class Meta:
        verbose_name = 'Catégorie de poisson'
        verbose_name_plural = 'Catégories de poissons'
        ordering = ['name']

    def __str__(self):
        return self.name


class ArrivalNote(models.Model):
    """
    Modèle pour la Note d'Arrivée (réception des lots de poissons)
    """
    STATUS_CHOICES = [
        ('draft', 'Brouillon'),
        ('accepted', 'Accepté'),
        ('in_progress', 'En traitement'),
        ('completed', 'Terminé'),
        ('suspended', 'Suspendu'),
        ('cancelled', 'Annulé'),
    ]

    # ID du LOT - Identifiant unique auto-généré sur 6+ chiffres
    lot_id = models.CharField(
        max_length=20,
        unique=True,
        verbose_name='ID du LOT',
        help_text='Identifiant unique généré automatiquement (ex: 000001, 000002, ...)'
    )

    # Client
    client = models.ForeignKey(
        'seafood.Client',
        on_delete=models.PROTECT,
        related_name='arrival_notes',
        verbose_name='Client'
    )

    # Date de réception
    reception_date = models.DateField(verbose_name='Date de réception')

    # Poids en kg
    weight = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name='Poids (kg)',
        help_text='Poids du lot en kilogrammes'
    )

    # Service demandé
    service_type = models.ForeignKey(
        Service,
        on_delete=models.PROTECT,
        related_name='arrival_notes',
        verbose_name='Type de service',
        help_text='Service à effectuer sur ce lot'
    )

    # Statut du lot
    status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        default='draft',
        verbose_name='Statut'
    )

    # Observations
    observations = models.TextField(
        blank=True,
        verbose_name='Observations',
        help_text='Notes ou remarques sur la réception'
    )

    # Motif de rejet (si status = rejected)
    rejection_reason = models.TextField(
        blank=True,
        verbose_name='Motif de rejet',
        help_text='Raison du rejet du lot'
    )

    # Métadonnées
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Date d\'ajout'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Date de modification'
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_arrival_notes',
        verbose_name='Créé par'
    )

    class Meta:
        verbose_name = 'Note d\'arrivée'
        verbose_name_plural = 'Notes d\'arrivée'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['lot_id']),
            models.Index(fields=['status']),
            models.Index(fields=['reception_date']),
            models.Index(fields=['client']),
        ]

    def __str__(self):
        return f"LOT {self.lot_id} - {self.client.name} - {self.reception_date}"

    def save(self, *args, **kwargs):
        # Générer le lot_id s'il n'existe pas
        if not self.lot_id:
            self.lot_id = self.generate_lot_id()
        super().save(*args, **kwargs)

    @staticmethod
    def generate_lot_id():
        """Génère un ID de lot unique au format XXXXXX (6+ chiffres)"""
        last_note = ArrivalNote.objects.order_by('-lot_id').first()

        if last_note and last_note.lot_id:
            try:
                # Extraire le numéro et l'incrémenter
                last_number = int(last_note.lot_id)
                new_number = last_number + 1
            except ValueError:
                # Si le format n'est pas un nombre, recommencer à 1
                new_number = 1
        else:
            # Première note d'arrivée
            new_number = 1

        # Formater avec au minimum 6 chiffres
        return f"{new_number:06d}"

    @property
    def is_transfer_only(self):
        """Vérifie si c'est un transfert simple (pas de traitement)"""
        # Vérifier par catégorie du service
        return self.service_type and self.service_type.category == 'transfer'

    @property
    def can_be_edited(self):
        """Vérifie si le lot peut être modifié"""
        return self.status == 'draft'

    @property
    def is_locked(self):
        """Vérifie si le lot est verrouillé (accepté et en circulation)"""
        return self.status in ['accepted', 'in_progress', 'completed']
