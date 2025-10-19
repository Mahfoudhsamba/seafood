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
        ('restaurant ', 'Restaurant'),
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


class Cashbox(models.Model):
    """
    Modèle pour la gestion des caisses
    """
    STATUS_CHOICES = [
        ('active', 'Actif'),
        ('inactive', 'Inactif'),
        ('suspended', 'Suspendu'),
    ]

    # Dossier (nom de la caisse)
    folder_code = models.CharField(
        max_length=200,
        verbose_name='Dossier',
        help_text='Nom de la caisse (ex: Technologie de l\'information)'
    )

    # Prefix unique pour la numérotation
    prefix = models.CharField(
        max_length=6,
        unique=True,
        verbose_name='Préfixe',
        help_text='Préfixe unique pour la numérotation des documents (max 6 caractères)'
    )

    # Description
    description = models.TextField(
        blank=True,
        verbose_name='Description',
        help_text='Description de la caisse'
    )

    # Statut
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active',
        verbose_name='Statut'
    )

    # Solde actuel
    current_balance = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0.00,
        verbose_name='Solde actuel'
    )

    # Dates
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Date de création')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Date de modification')
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Créé par'
    )

    class Meta:
        verbose_name = 'Caisse'
        verbose_name_plural = 'Caisses'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.folder_code} - {self.description if self.description else 'Sans description'}"


def cashbox_transaction_attachment_path(instance, filename):
    """Génère le chemin pour les pièces jointes des transactions de caisse"""
    return f'cashbox_transactions/cashbox_{instance.cashbox_id}/{filename}'


class CashboxTransaction(models.Model):
    """
    Modèle pour les transactions de caisse (alimentations et sorties)
    """
    TRANSACTION_TYPE_CHOICES = [
        ('in', 'Entrée (Alimentation)'),
        ('out', 'Sortie'),
    ]

    SOURCE_CHOICES = [
        ('cash', 'Cash (Espèces)'),
        ('mobile_transfer', 'Transfert mobile'),
        ('check', 'Chèque'),
        ('deposit', 'Versement'),
        ('bank_transfer', 'Virement bancaire'),
        ('other', 'Autre'),
    ]

    # Référence de transaction
    transaction_number = models.CharField(
        max_length=20,
        unique=True,
        verbose_name='Numéro de transaction',
        help_text='Format: TRXXXXXXX (généré automatiquement)'
    )

    # Caisse concernée
    cashbox = models.ForeignKey(
        Cashbox,
        on_delete=models.PROTECT,
        related_name='transactions',
        verbose_name='Caisse'
    )

    # Type de transaction
    transaction_type = models.CharField(
        max_length=3,
        choices=TRANSACTION_TYPE_CHOICES,
        verbose_name='Type de transaction'
    )

    # Source/Mode
    source = models.CharField(
        max_length=20,
        choices=SOURCE_CHOICES,
        verbose_name='Source/Mode'
    )

    # Montant
    amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name='Montant'
    )

    # Date de transaction
    transaction_date = models.DateField(verbose_name='Date de transaction')

    # Compte bancaire (si applicable)
    bank_account = models.ForeignKey(
        'BankAccount',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Compte bancaire'
    )

    # Description
    description = models.TextField(
        blank=True,
        verbose_name='Description',
        help_text='Motif de la transaction'
    )

    # Champs spécifiques pour transfert mobile
    transaction_id = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='ID Transaction',
        help_text='Identifiant de la transaction (pour transfert mobile)'
    )

    # Champs spécifiques pour chèque, versement et virement
    check_number = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='Numéro de chèque/versement',
        help_text='Numéro du chèque ou du versement'
    )
    issuing_bank = models.ForeignKey(
        'BankAccount',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='issued_transactions',
        verbose_name='Banque émettrice'
    )
    check_date = models.DateField(
        blank=True,
        null=True,
        verbose_name='Date du chèque/versement'
    )

    # Référence pour virement
    transfer_reference = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Référence de virement',
        help_text='Référence du virement bancaire'
    )

    # Pièce justificative
    justification = models.FileField(
        upload_to=cashbox_transaction_attachment_path,
        blank=True,
        null=True,
        verbose_name='Pièce justificative',
        help_text='Document justifiant la transaction (optionnel)'
    )

    # Solde après transaction
    balance_after = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name='Solde après transaction'
    )

    # Dates et utilisateur
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Date de création')
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Créé par'
    )

    class Meta:
        verbose_name = 'Transaction de caisse'
        verbose_name_plural = 'Transactions de caisse'
        ordering = ['-transaction_date', '-created_at']
        indexes = [
            models.Index(fields=['transaction_number']),
            models.Index(fields=['cashbox', 'transaction_date']),
            models.Index(fields=['transaction_type']),
        ]

    def __str__(self):
        return f"{self.transaction_number} - {self.cashbox.folder_code} - {self.amount} MRU"

    def save(self, *args, **kwargs):
        # Générer le numéro de transaction s'il n'existe pas
        if not self.transaction_number:
            self.transaction_number = self.generate_transaction_number()

        # Calculer le nouveau solde
        if self.transaction_type == 'in':
            self.balance_after = self.cashbox.current_balance + self.amount
        else:  # out
            self.balance_after = self.cashbox.current_balance - self.amount

        super().save(*args, **kwargs)

        # Mettre à jour le solde de la caisse
        self.cashbox.current_balance = self.balance_after
        self.cashbox.save()

    @staticmethod
    def generate_transaction_number():
        """Génère un numéro de transaction unique"""
        last_transaction = CashboxTransaction.objects.order_by('-transaction_number').first()
        if last_transaction and last_transaction.transaction_number:
            # Extraire le numéro et l'incrémenter
            # Supporter l'ancien format avec tiret et le nouveau sans tiret
            if '-' in last_transaction.transaction_number:
                last_number = int(last_transaction.transaction_number.split('-')[1])
            else:
                last_number = int(last_transaction.transaction_number[3:])
            new_number = last_number + 1
        else:
            # Première transaction
            new_number = 1

        # Format: TRX000001 (sans tiret ni espace)
        return f"TRX{new_number:06d}"


@receiver(pre_delete, sender=CashboxTransaction)
def delete_cashbox_transaction_file_on_delete(sender, instance, **kwargs):
    """Supprime le fichier justificatif lors de la suppression de la transaction"""
    if instance.justification and os.path.isfile(instance.justification.path):
        os.remove(instance.justification.path)


def bank_account_attachment_path(instance, filename):
    """Génère le chemin pour les pièces jointes du compte bancaire"""
    ext = filename.split('.')[-1].lower()
    if instance.pk:
        return f'bank_accounts/account_{instance.pk}/{filename}'
    return f'bank_accounts/{filename}'


class BankAccount(models.Model):
    """
    Modèle pour la gestion des comptes bancaires
    """
    ACCOUNT_TYPE_CHOICES = [
        ('checking', 'Compte courant'),
        ('savings', 'Compte épargne'),
        ('merchant', 'Compte marchand'),
        ('virtual', 'Compte virtuel'),
    ]

    CATEGORY_CHOICES = [
        ('classic', 'Classique'),
        ('bank_mobile', 'Banque mobile'),
        ('neo_bank', 'Néo-banque'),
        ('payment_gateway', 'Passerelle de paiement'),
        ('e_wallet', 'Portefeuille électronique'),
    ]

    CURRENCY_CHOICES = [
        ('MRU', 'Ouguiya (MRU)'),
        ('USD', 'Dollar américain (USD)'),
        ('EUR', 'Euro (EUR)'),
        ('CAD', 'Dollar canadien (CAD)'),
    ]

    STATUS_CHOICES = [
        ('active', 'Actif'),
        ('inactive', 'Inactif'),
        ('closed', 'Fermé'),
        ('frozen', 'Gelé'),
    ]

    # Identifiant unique
    bank_identifier = models.CharField(
        max_length=9,
        unique=True,
        verbose_name='Identifiant bancaire',
        help_text='Format: BNK + 6 chiffres (généré automatiquement)'
    )

    # Informations de base
    bank_name = models.CharField(max_length=200, verbose_name='Nom de la banque')
    account_number = models.CharField(max_length=50, verbose_name='Numéro de compte')
    iban = models.CharField(
        max_length=34,
        blank=True,
        verbose_name='IBAN',
        help_text='International Bank Account Number'
    )
    agency = models.CharField(max_length=200, blank=True, verbose_name='Agence')

    # Type et catégorie
    account_type = models.CharField(
        max_length=20,
        choices=ACCOUNT_TYPE_CHOICES,
        default='checking',
        verbose_name='Type de compte'
    )
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default='classic',
        verbose_name='Catégorie'
    )

    # Devise
    currency = models.CharField(
        max_length=3,
        choices=CURRENCY_CHOICES,
        default='MRU',
        verbose_name='Devise'
    )

    # Statut
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active',
        verbose_name='Statut'
    )

    # Contact et administratif
    account_holder = models.CharField(
        max_length=200,
        verbose_name='Titulaire du compte'
    )
    phone = models.CharField(
        max_length=17,
        blank=True,
        verbose_name='Téléphone'
    )
    email = models.EmailField(blank=True, verbose_name='Email')
    address = models.TextField(blank=True, verbose_name='Adresse')

    # Pièces jointes
    rib_scan = models.FileField(
        upload_to=bank_account_attachment_path,
        blank=True,
        null=True,
        verbose_name='Scan RIB',
        help_text='Relevé d\'Identité Bancaire'
    )
    contract = models.FileField(
        upload_to=bank_account_attachment_path,
        blank=True,
        null=True,
        verbose_name='Contrat'
    )

    # Solde actuel
    current_balance = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0.00,
        verbose_name='Solde actuel'
    )

    # Dates
    account_opening_date = models.DateField(
        verbose_name='Date d\'ouverture du compte'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Date de création')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Date de modification')
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Créé par'
    )

    class Meta:
        verbose_name = 'Compte bancaire'
        verbose_name_plural = 'Comptes bancaires'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['bank_identifier']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.bank_identifier} - {self.bank_name} ({self.account_number})"

    def save(self, *args, **kwargs):
        # Générer l'identifiant bancaire s'il n'existe pas
        if not self.bank_identifier:
            self.bank_identifier = self.generate_bank_identifier()
        super().save(*args, **kwargs)

    @staticmethod
    def generate_bank_identifier():
        """Génère un identifiant bancaire unique au format BNK + 6 chiffres"""
        last_account = BankAccount.objects.order_by('-bank_identifier').first()
        if last_account and last_account.bank_identifier:
            # Extraire le numéro et l'incrémenter
            last_number = int(last_account.bank_identifier[3:])
            new_number = last_number + 1
        else:
            # Premier compte
            new_number = 1

        # Formater avec 6 chiffres
        return f"BNK{new_number:06d}"


@receiver(pre_delete, sender=BankAccount)
def delete_bank_account_files_on_delete(sender, instance, **kwargs):
    """Supprime les fichiers lors de la suppression du compte bancaire"""
    if instance.rib_scan and os.path.isfile(instance.rib_scan.path):
        os.remove(instance.rib_scan.path)
    if instance.contract and os.path.isfile(instance.contract.path):
        os.remove(instance.contract.path)


class PurchaseRequest(models.Model):
    """
    Modèle pour les demandes d'achat (Purchase Request)
    """
    STATUS_CHOICES = [
        ('draft', 'Brouillon'),
        ('approved', 'Accepté'),
        ('rejected', 'Rejeté'),
        ('cancelled', 'Annulé'),
    ]

    # Numéro de PR
    pr_number = models.CharField(
        max_length=20,
        unique=True,
        verbose_name='Numéro PR',
        help_text='Format: #PRMMYYXXXXXX (généré automatiquement)'
    )

    # Date de la demande
    pr_date = models.DateField(verbose_name='Date PR')

    # Informations du demandeur
    requester_first_name = models.CharField(max_length=100, verbose_name='Prénom du demandeur')
    requester_last_name = models.CharField(max_length=100, verbose_name='Nom du demandeur')
    position = models.CharField(max_length=100, verbose_name='Position')
    requester_phone = models.CharField(max_length=17, verbose_name='Téléphone du demandeur')

    # Échéance
    deadline = models.DateField(verbose_name='Échéance de la demande')

    # Description
    description = models.TextField(blank=True, verbose_name='Description')

    # Statut et motif
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
        verbose_name='Statut'
    )
    rejection_reason = models.TextField(
        blank=True,
        verbose_name='Motif de rejet',
        help_text='Obligatoire si le statut est "Rejeté"'
    )

    # Dates
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Date de création')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Date de modification')
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Créé par'
    )

    class Meta:
        verbose_name = 'Demande d\'achat'
        verbose_name_plural = 'Demandes d\'achat'
        ordering = ['-pr_date', '-created_at']
        indexes = [
            models.Index(fields=['pr_number']),
            models.Index(fields=['status']),
            models.Index(fields=['pr_date']),
        ]

    def __str__(self):
        return f"PR-{self.pr_number}"

    def save(self, *args, **kwargs):
        from django.db import transaction, IntegrityError

        # Générer le numéro PR s'il n'existe pas
        if not self.pr_number:
            max_attempts = 10
            for attempt in range(max_attempts):
                try:
                    with transaction.atomic():
                        self.pr_number = self.generate_pr_number()
                        super().save(*args, **kwargs)
                    return  # Succès, sortir de la méthode
                except IntegrityError:
                    if attempt == max_attempts - 1:
                        # Dernière tentative échouée
                        raise
                    # Réessayer avec un nouveau numéro
                    self.pr_number = None
                    continue
        else:
            super().save(*args, **kwargs)

    @staticmethod
    def generate_pr_number():
        """Génère un numéro PR unique au format #PRMMYYXXXXXX"""
        from django.utils import timezone
        from django.db.models import Max

        now = timezone.now()
        month = now.strftime('%m')  # Mois sur 2 chiffres
        year = now.strftime('%y')   # Année sur 2 chiffres (ex: 25 pour 2025)
        prefix = f"PR{month}{year}"   # Ex: PR1025 pour octobre 2025
        prefix_with_hash = f"#{prefix}"  # Ex: #PR1025

        # Chercher le dernier PR du mois/année en cours avec agrégation
        last_pr = PurchaseRequest.objects.filter(
            pr_number__startswith=prefix_with_hash
        ).order_by('-pr_number').first()

        if last_pr and last_pr.pr_number:
            # Extraire le numéro et l'incrémenter
            last_number = int(last_pr.pr_number[-6:])
            new_number = last_number + 1
        else:
            # Première demande du mois
            new_number = 1

        # Format: #PRMMYYXXXXXX (ex: #PR1025000001)
        return f"{prefix_with_hash}{new_number:06d}"

    @property
    def requester_full_name(self):
        """Retourne le nom complet du demandeur"""
        return f"{self.requester_first_name} {self.requester_last_name}"


class PurchaseRequestItem(models.Model):
    """
    Modèle pour les lignes d'articles d'une demande d'achat
    """
    UNIT_CHOICES = [
        ('pieces', 'Pièces'),
        ('bags', 'Sacs'),
        ('boxes', 'Boîtes'),
        ('foot', 'Pieds'),
        ('meter', 'Mètres'),
        ('pairs', 'Paires'),
        ('reams', 'Rames'),
        ('rolls', 'Rouleaux'),
        ('sets', 'Ensembles'),
        ('square_meters', 'Mètres carrés'),
        ('square_feet', 'Pieds carrés'),
        ('tons', 'Tonnes'),
    ]

    # Demande d'achat parente
    purchase_request = models.ForeignKey(
        PurchaseRequest,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='Demande d\'achat'
    )

    # Désignation et quantité
    designation = models.CharField(max_length=200, verbose_name='Désignation')
    quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Quantité'
    )
    unit = models.CharField(
        max_length=20,
        choices=UNIT_CHOICES,
        default='pieces',
        verbose_name='Unité'
    )

    # Ordre d'affichage
    order = models.PositiveIntegerField(default=0, verbose_name='Ordre')

    class Meta:
        verbose_name = 'Ligne de demande d\'achat'
        verbose_name_plural = 'Lignes de demandes d\'achat'
        ordering = ['order', 'id']

    def __str__(self):
        return f"{self.designation} - {self.quantity} {self.get_unit_display()}"


def purchase_order_file_path(instance, filename):
    """Génère le chemin pour les fichiers des bons de commande"""
    return f'purchase_orders/po_{instance.po_number}/{filename}'


class PurchaseOrder(models.Model):
    """
    Modèle pour les bons de commande (Purchase Order)
    """
    STATUS_CHOICES = [
        ('draft', 'Brouillon'),
        ('pending', 'En attente'),
        ('approved', 'Approuvé'),
        ('paid', 'Payé'),
        ('cancelled', 'Annulé'),
    ]

    # Numéro de PO
    po_number = models.CharField(
        max_length=20,
        unique=True,
        verbose_name='Numéro PO',
        help_text='Numéro unique du bon de commande (généré automatiquement)'
    )

    PAYMENT_METHOD_CHOICES = [
        ('cashbox', 'Caisse'),
        ('bank', 'Compte bancaire'),
    ]

    # Dates
    po_date = models.DateField(verbose_name='Date PO')
    payment_date = models.DateField(
        blank=True,
        null=True,
        verbose_name='Date de paiement'
    )

    # Paiement
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        blank=True,
        null=True,
        verbose_name='Méthode de paiement'
    )
    payment_cashbox = models.ForeignKey(
        Cashbox,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name='purchase_order_payments',
        verbose_name='Caisse de paiement'
    )
    payment_bank = models.ForeignKey(
        BankAccount,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        verbose_name='Compte bancaire de paiement'
    )

    # Fichier attaché
    file = models.FileField(
        upload_to=purchase_order_file_path,
        blank=True,
        null=True,
        verbose_name='Fichier'
    )

    # Fournisseur
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.PROTECT,
        verbose_name='Fournisseur'
    )

    # Totaux (calculés à partir des items)
    subtotal = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0.00,
        verbose_name='Sous-total'
    )
    tax_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0.00,
        verbose_name='Montant taxe'
    )
    total = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0.00,
        verbose_name='Total'
    )

    # Note
    note = models.TextField(blank=True, verbose_name='Note')

    # Statut
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
        verbose_name='Statut'
    )

    # Approbation
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_purchase_orders',
        verbose_name='Approuvé par'
    )
    approved_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Date d\'approbation'
    )

    # Dates
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Date de création')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Date de modification')
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_purchase_orders',
        verbose_name='Créé par'
    )

    class Meta:
        verbose_name = 'Bon de commande'
        verbose_name_plural = 'Bons de commande'
        ordering = ['-po_date', '-created_at']
        indexes = [
            models.Index(fields=['po_number']),
            models.Index(fields=['status']),
            models.Index(fields=['po_date']),
        ]

    def __str__(self):
        return f"{self.po_number} - {self.supplier.name}"

    def save(self, *args, **kwargs):
        from django.db import transaction, IntegrityError

        # Générer le numéro PO s'il n'existe pas
        if not self.po_number:
            max_attempts = 10
            for attempt in range(max_attempts):
                try:
                    with transaction.atomic():
                        self.po_number = self.generate_po_number()
                        super().save(*args, **kwargs)
                    return  # Succès, sortir de la méthode
                except IntegrityError:
                    if attempt == max_attempts - 1:
                        # Dernière tentative échouée
                        raise
                    # Réessayer avec un nouveau numéro
                    self.po_number = None
                    continue
        else:
            super().save(*args, **kwargs)

    def calculate_totals(self):
        """Calculer les totaux à partir des items"""
        from decimal import Decimal

        self.subtotal = Decimal('0.00')
        self.tax_amount = Decimal('0.00')

        for item in self.items.all():
            item_subtotal = item.quantity * item.unit_price
            item_tax = (item_subtotal * item.tax_rate) / 100

            self.subtotal += item_subtotal
            self.tax_amount += item_tax

        self.total = self.subtotal + self.tax_amount
        self.save()

    @staticmethod
    def generate_po_number():
        """Génère un numéro PO unique au format #MMYYXXXXXX"""
        from django.utils import timezone
        from django.db.models import Max

        now = timezone.now()
        month = now.strftime('%m')  # Mois sur 2 chiffres
        year = now.strftime('%y')   # Année sur 2 chiffres (ex: 25 pour 2025)
        prefix = f"#{month}{year}"   # Ex: #1025 pour octobre 2025

        # Chercher le dernier PO du mois/année en cours
        last_po = PurchaseOrder.objects.filter(
            po_number__startswith=prefix
        ).order_by('-po_number').first()

        if last_po and last_po.po_number:
            # Extraire le numéro et l'incrémenter
            last_number = int(last_po.po_number[-6:])
            new_number = last_number + 1
        else:
            # Premier bon de commande du mois
            new_number = 1

        # Format: #MMYYXXXXXX (ex: #1025000001)
        return f"{prefix}{new_number:06d}"


class PurchaseOrderItem(models.Model):
    """
    Modèle pour les lignes d'articles d'un bon de commande
    """
    UNIT_CHOICES = [
        ('pieces', 'Pièces'),
        ('bags', 'Sacs'),
        ('boxes', 'Boîtes'),
        ('foot', 'Pieds'),
        ('meter', 'Mètres'),
        ('pairs', 'Paires'),
        ('reams', 'Rames'),
        ('rolls', 'Rouleaux'),
        ('sets', 'Ensembles'),
        ('square_meters', 'Mètres carrés'),
        ('square_feet', 'Pieds carrés'),
        ('tons', 'Tonnes'),
    ]

    # Bon de commande parent
    purchase_order = models.ForeignKey(
        PurchaseOrder,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='Bon de commande'
    )

    # Désignation et quantité
    designation = models.CharField(max_length=200, verbose_name='Désignation')
    quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Quantité'
    )
    unit = models.CharField(
        max_length=20,
        choices=UNIT_CHOICES,
        default='pieces',
        verbose_name='Unité'
    )

    # Prix
    unit_price = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name='Prix unitaire'
    )

    # Taxe
    tax_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        verbose_name='Taux de taxe (%)'
    )

    # Ordre d'affichage
    order = models.PositiveIntegerField(default=0, verbose_name='Ordre')

    class Meta:
        verbose_name = 'Ligne de bon de commande'
        verbose_name_plural = 'Lignes de bons de commande'
        ordering = ['order', 'id']

    def __str__(self):
        return f"{self.designation} - {self.quantity} {self.get_unit_display()}"

    @property
    def item_subtotal(self):
        """Calcule le sous-total de l'item"""
        return self.quantity * self.unit_price

    @property
    def item_tax_amount(self):
        """Calcule le montant de taxe de l'item"""
        return (self.item_subtotal * self.tax_rate) / 100

    @property
    def item_total(self):
        """Calcule le total de l'item"""
        return self.item_subtotal + self.item_tax_amount


@receiver(pre_delete, sender=PurchaseOrder)
def delete_purchase_order_file_on_delete(sender, instance, **kwargs):
    """Supprime le fichier lors de la suppression du bon de commande"""
    if instance.file and os.path.isfile(instance.file.path):
        os.remove(instance.file.path)
