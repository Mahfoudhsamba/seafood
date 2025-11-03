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


class ServiceSubCategory(models.Model):
    """
    Modèle pour les sous-catégories de services
    """
    STATUS_CHOICES = [
        ('active', 'Actif'),
        ('suspended', 'Suspendu'),
    ]

    # Catégorie parente
    category = models.ForeignKey(
        ServiceCategory,
        on_delete=models.CASCADE,
        related_name='subcategories',
        verbose_name='Catégorie'
    )

    # Nom de la sous-catégorie (requis)
    name = models.CharField(
        max_length=200,
        verbose_name='Nom de la sous-catégorie'
    )

    # Poids (optionnel)
    weight = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name='Poids (kg)',
        help_text='Poids en kilogrammes (optionnel)'
    )

    # Prix (optionnel)
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name='Prix',
        help_text='Prix en devise locale (optionnel)'
    )

    # Description (optionnelle)
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
        related_name='created_service_subcategories',
        verbose_name='Créé par'
    )

    class Meta:
        verbose_name = 'Sous-catégorie de service'
        verbose_name_plural = 'Sous-catégories de services'
        ordering = ['category', 'name']
        unique_together = [['category', 'name']]
        indexes = [
            models.Index(fields=['category']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.category.name} - {self.name}"

    @property
    def is_active(self):
        """Vérifie si la sous-catégorie est active"""
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


class Reception(models.Model):
    """
    Modèle pour la Note d'Arrivée (réception des lots de poissons)
    """
    STATUS_CHOICES = [
        ('draft', 'Brouillon'),
        ('accepted', 'Accepté'),
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
        db_table = 'operations_reception'
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
        last_note = Reception.objects.order_by('-lot_id').first()

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
        return self.status in ['accepted', 'completed']


class Report(models.Model):
    """
    Modèle pour le rapport de réception des poissons reçus
    Contient les détails par espèce avec les poids,
    incluant les poissons rejetés et les poids perdus
    """
    STATUS_CHOICES = [
        ('draft', 'Brouillon'),
        ('validated', 'Validé'),
        ('cancelled', 'Annulé'),
    ]

    # Numéro du lot (Note d'arrivée)
    arrival_note = models.ForeignKey(
        Reception,
        on_delete=models.PROTECT,
        related_name='reports',
        verbose_name='Lot (Note d\'arrivée)',
        help_text='Sélectionner un lot dont le type de service est supérieur à 1003'
    )

    # Date du rapport
    report_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Date du rapport'
    )

    # Observation générale
    general_observation = models.TextField(
        blank=True,
        verbose_name='Observation générale',
        help_text='Remarques générales sur le rapport du lot'
    )

    # Statut
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
        verbose_name='Statut'
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
        related_name='created_reports',
        verbose_name='Créé par'
    )

    class Meta:
        db_table = 'operations_report'
        verbose_name = 'Rapport de réception'
        verbose_name_plural = 'Rapports de réception'
        ordering = ['-report_date']
        indexes = [
            models.Index(fields=['arrival_note']),
            models.Index(fields=['report_date']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"Rapport LOT {self.arrival_note.lot_id} - {self.report_date.strftime('%d/%m/%Y %H:%M')}"

    @property
    def total_weight(self):
        """Calcule le poids total de tous les items du rapport"""
        return sum(item.weight for item in self.items.all())

    @property
    def can_be_edited(self):
        """Vérifie si le rapport peut être modifié"""
        return self.status == 'draft'


class ReportItem(models.Model):
    """
    Modèle pour les détails par espèce du rapport de réception
    Chaque item représente une espèce de poisson avec son poids et commentaires
    """
    SPECIES_CHOICES = [
        ('sardine', 'Sardine'),
        ('maquereau', 'Maquereau'),
        ('anchois', 'Anchois'),
        ('thon', 'Thon'),
        ('espadon', 'Espadon'),
        ('dorade', 'Dorade'),
        ('loup', 'Loup (Bar)'),
        ('crevette', 'Crevette'),
        ('calmar', 'Calmar'),
        ('poulpe', 'Poulpe'),
        ('rejete', 'Poisson rejeté'),
        ('perdu', 'Poids perdu'),
        ('autre', 'Autre espèce'),
    ]

    # Rapport de réception parent
    report = models.ForeignKey(
        Report,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='Rapport de réception'
    )

    # Espèce de poisson
    species = models.CharField(
        max_length=100,
        choices=SPECIES_CHOICES,
        verbose_name='Espèce',
        help_text='Type de poisson ou catégorie'
    )

    # Nom personnalisé de l'espèce (si "autre" est sélectionné)
    custom_species_name = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Nom personnalisé de l\'espèce',
        help_text='Utilisé si "Autre espèce" est sélectionné'
    )

    # Poids en kg
    weight = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name='Poids (kg)',
        help_text='Poids de cette espèce en kilogrammes'
    )

    # Commentaire
    comment = models.TextField(
        blank=True,
        verbose_name='Commentaire',
        help_text='Remarques spécifiques sur cette espèce'
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

    class Meta:
        db_table = 'operations_reportitem'
        verbose_name = 'Détail par espèce'
        verbose_name_plural = 'Détails par espèce'
        ordering = ['report', 'species']
        indexes = [
            models.Index(fields=['report']),
            models.Index(fields=['species']),
        ]

    def __str__(self):
        species_display = self.get_species_display()
        if self.species == 'autre' and self.custom_species_name:
            species_display = self.custom_species_name
        return f"{species_display} - {self.weight} kg"

    @property
    def species_name(self):
        """Retourne le nom de l'espèce (personnalisé ou prédéfini)"""
        if self.species == 'autre' and self.custom_species_name:
            return self.custom_species_name
        return self.get_species_display()


class Classification(models.Model):
    """
    Modèle pour la classification d'un rapport de réception
    Permet de classifier les poissons par espèce avec le nombre de plats et poids
    """
    STATUS_CHOICES = [
        ('draft', 'Brouillon'),
        ('validated', 'Validé'),
        ('in_tunnel', 'In tunnel'),
        ('completed', 'Terminé'),
        ('cancelled', 'Annulé'),
    ]

    # Numéro du rapport (lié à la réception)
    reception = models.ForeignKey(
        Reception,
        on_delete=models.PROTECT,
        related_name='classifications',
        verbose_name='Réception (LOT)',
        help_text='Note d\'arrivée à classifier'
    )

    # Nom complet du pointeur
    pointer_full_name = models.CharField(
        max_length=200,
        verbose_name='Nom complet du pointeur',
        help_text='Nom de la personne effectuant la classification'
    )

    # Référence de la chambre
    reference_chambre = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name='Référence de la chambre',
        help_text='Référence de la chambre froide'
    )

    # Date et heure de début
    start_datetime = models.DateTimeField(
        verbose_name='Date et heure de début',
        help_text='Début de la classification'
    )

    # Date et heure de fin
    end_datetime = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Date et heure de fin',
        help_text='Fin de la classification'
    )

    # Date et heure d'entrée dans le tunnel
    tunnel_in = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Entrée tunnel',
        help_text='Date et heure d\'entrée dans le tunnel'
    )

    # Date et heure de sortie du tunnel
    tunnel_out = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Sortie tunnel',
        help_text='Date et heure de sortie du tunnel'
    )

    # Statut
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
        verbose_name='Statut'
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
        related_name='created_classifications',
        verbose_name='Créé par'
    )

    class Meta:
        db_table = 'operations_classification'
        verbose_name = 'Classification'
        verbose_name_plural = 'Classifications'
        ordering = ['-start_datetime', '-created_at']
        indexes = [
            models.Index(fields=['reception']),
            models.Index(fields=['start_datetime']),
            models.Index(fields=['end_datetime']),
            models.Index(fields=['tunnel_in']),
            models.Index(fields=['tunnel_out']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"Classification LOT {self.reception.lot_id} - {self.start_datetime.strftime('%d/%m/%Y %H:%M')}"

    def clean(self):
        """Validation personnalisée"""
        super().clean()

        # Vérifier que la date de fin est après la date de début
        if self.start_datetime and self.end_datetime:
            if self.end_datetime <= self.start_datetime:
                raise ValidationError({
                    'end_datetime': 'La date de fin doit être postérieure à la date de début.'
                })

        # Vérifier que tunnel_out est après tunnel_in
        if self.tunnel_in and self.tunnel_out:
            if self.tunnel_out <= self.tunnel_in:
                raise ValidationError({
                    'tunnel_out': 'La date de sortie du tunnel doit être postérieure à l\'entrée.'
                })

        # Vérifier que la réception a un rapport
        if self.reception and not self.reception.reports.exists():
            raise ValidationError({
                'reception': 'Cette réception doit avoir un rapport avant de pouvoir créer une classification.'
            })

    @property
    def total_weight(self):
        """Calcule le poids total de tous les items de la classification"""
        return sum(item.weight for item in self.items.all())

    @property
    def total_plates(self):
        """Calcule le nombre total de plats de tous les items"""
        return sum(item.plate_count for item in self.items.all())

    @property
    def can_be_edited(self):
        """Vérifie si la classification peut être modifiée (seulement en brouillon)"""
        return self.status == 'draft'

    @property
    def can_be_deleted(self):
        """Vérifie si la classification peut être supprimée (seulement en brouillon)"""
        return self.status == 'draft'

    def get_allowed_next_statuses(self):
        """Retourne les statuts suivants autorisés selon le statut actuel"""
        status_transitions = {
            'draft': ['validated', 'cancelled'],
            'validated': ['in_tunnel', 'cancelled'],
            'in_tunnel': ['completed', 'cancelled'],
            'completed': [],  # Statut final
            'cancelled': [],  # Statut final
        }
        return status_transitions.get(self.status, [])

    def can_transition_to(self, new_status):
        """Vérifie si la transition vers le nouveau statut est autorisée"""
        return new_status in self.get_allowed_next_statuses()

    @property
    def duration(self):
        """Calcule la durée de la classification"""
        if self.start_datetime and self.end_datetime:
            delta = self.end_datetime - self.start_datetime
            hours = int(delta.total_seconds() // 3600)
            minutes = int((delta.total_seconds() % 3600) // 60)
            return f"{hours}h{minutes:02d}min"
        return None

    @property
    def tunnel_duration(self):
        """Calcule la durée dans le tunnel"""
        if self.tunnel_in and self.tunnel_out:
            delta = self.tunnel_out - self.tunnel_in
            hours = int(delta.total_seconds() // 3600)
            minutes = int((delta.total_seconds() % 3600) // 60)
            return f"{hours}h{minutes:02d}min"
        return None


class ClassificationItem(models.Model):
    """
    Modèle pour les détails par espèce de la classification
    Chaque item représente une espèce avec son nombre de plats et poids
    """

    # Classification parent
    classification = models.ForeignKey(
        Classification,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='Classification'
    )

    # Espèce (sous-catégorie de service)
    species = models.ForeignKey(
        ServiceSubCategory,
        on_delete=models.PROTECT,
        related_name='classification_items',
        verbose_name='Espèce',
        help_text='Sous-catégorie de service représentant l\'espèce'
    )

    # Nombre de plats
    plate_count = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name='Nombre de plats',
        help_text='Nombre de plats pour cette espèce'
    )

    # Poids en kg
    weight = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name='Poids (kg)',
        help_text='Poids total de cette espèce en kilogrammes'
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

    class Meta:
        db_table = 'operations_classificationitem'
        verbose_name = 'Détail de classification'
        verbose_name_plural = 'Détails de classification'
        ordering = ['classification', 'species']
        indexes = [
            models.Index(fields=['classification']),
            models.Index(fields=['species']),
        ]
        # Éviter les doublons d'espèce dans une même classification
        unique_together = [['classification', 'species']]

    def __str__(self):
        return f"{self.species.name} - {self.plate_count} plats - {self.weight} kg"

    @property
    def average_weight_per_plate(self):
        """Calcule le poids moyen par plat"""
        if self.plate_count > 0:
            return self.weight / self.plate_count
        return Decimal('0.00')
