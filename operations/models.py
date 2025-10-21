from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from decimal import Decimal

# Create your models here.


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
    SERVICE_CHOICES = [
        ('transfer', 'Transfert (stockage)'),
        ('transfer_packaging', 'Transfert & Emballage'),
        ('treatment', 'Traitement'),
        ('complete_treatment', 'Traitement complet'),
    ]

    STATUS_CHOICES = [
        ('received', 'Reçu'),
        ('in_classification', 'En classification'),
        ('classified', 'Classifié'),
        ('rejected', 'Rejeté'),
        ('in_treatment', 'En traitement'),
        ('completed', 'Terminé'),
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
    service_type = models.CharField(
        max_length=50,
        choices=SERVICE_CHOICES,
        verbose_name='Type de service'
    )

    # Catégorie de poissons
    fish_category = models.ForeignKey(
        FishCategory,
        on_delete=models.PROTECT,
        related_name='arrival_notes',
        verbose_name='Catégorie de poisson'
    )

    # Statut du lot
    status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        default='received',
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
        return self.service_type == 'transfer'

    @property
    def needs_classification(self):
        """Vérifie si le lot nécessite une classification"""
        return self.service_type in ['treatment', 'complete_treatment'] and self.status == 'received'

    @property
    def can_be_classified(self):
        """Vérifie si le lot peut être classifié"""
        return self.status in ['received', 'in_classification']
