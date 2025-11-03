# Generated manually on 2025-11-03
# Migration pour rendre start_datetime NOT NULL

from django.db import migrations, models


def fill_start_datetime(apps, schema_editor):
    """Remplir start_datetime avec created_at pour les lignes NULL"""
    Classification = apps.get_model('operations', 'Classification')
    for classification in Classification.objects.filter(start_datetime__isnull=True).order_by():
        classification.start_datetime = classification.created_at
        classification.save(update_fields=['start_datetime'])


class Migration(migrations.Migration):

    dependencies = [
        ('operations', '0014_restore_start_datetime_remove_classification_date'),
    ]

    operations = [
        migrations.RunPython(fill_start_datetime, reverse_code=migrations.RunPython.noop),
        migrations.AlterField(
            model_name='classification',
            name='start_datetime',
            field=models.DateTimeField(help_text='Début de la classification', verbose_name='Date et heure de début'),
        ),
    ]
