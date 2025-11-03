# Generated manually on 2025-11-03
# Migration pour ajouter reference_chambre, tunnel_in, tunnel_out et nouveaux statuts

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('operations', '0015_make_start_datetime_required'),
    ]

    operations = [
        # Ajouter reference_chambre
        migrations.AddField(
            model_name='classification',
            name='reference_chambre',
            field=models.CharField(default='', help_text='Référence de la chambre froide', max_length=100, verbose_name='Référence de la chambre'),
            preserve_default=False,
        ),
        # Ajouter tunnel_in
        migrations.AddField(
            model_name='classification',
            name='tunnel_in',
            field=models.DateTimeField(blank=True, help_text="Date et heure d'entrée dans le tunnel", null=True, verbose_name='Entrée tunnel'),
        ),
        # Ajouter tunnel_out
        migrations.AddField(
            model_name='classification',
            name='tunnel_out',
            field=models.DateTimeField(blank=True, help_text='Date et heure de sortie du tunnel', null=True, verbose_name='Sortie tunnel'),
        ),
        # Modifier le champ status pour ajouter les nouveaux choix
        migrations.AlterField(
            model_name='classification',
            name='status',
            field=models.CharField(
                choices=[
                    ('draft', 'Brouillon'),
                    ('validated', 'Validé'),
                    ('in_tunnel', 'In tunnel'),
                    ('completed', 'Terminé'),
                    ('cancelled', 'Annulé')
                ],
                default='draft',
                max_length=20,
                verbose_name='Statut'
            ),
        ),
    ]
