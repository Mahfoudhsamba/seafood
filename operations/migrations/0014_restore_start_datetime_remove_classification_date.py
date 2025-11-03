# Generated manually on 2025-11-03
# Migration pour revenir à la structure originale: start_datetime et end_datetime

from django.db import migrations, models


def restore_structure(apps, schema_editor):
    """
    Restauration de la structure originale:
    1. Supprimer l'index sur classification_date
    2. Ajuster les indexes
    """
    with schema_editor.connection.cursor() as cursor:
        # Supprimer l'index sur classification_date s'il existe
        cursor.execute("""
            SELECT COUNT(*)
            FROM information_schema.STATISTICS
            WHERE TABLE_SCHEMA = DATABASE()
            AND TABLE_NAME = 'operations_classification'
            AND INDEX_NAME = 'operations__classif_date_idx'
        """)
        if cursor.fetchone()[0] > 0:
            print("Suppression de l'index sur classification_date...")
            cursor.execute("DROP INDEX operations__classif_date_idx ON operations_classification")

        # Ajouter l'index sur start_datetime s'il n'existe pas
        cursor.execute("""
            SELECT COUNT(*)
            FROM information_schema.STATISTICS
            WHERE TABLE_SCHEMA = DATABASE()
            AND TABLE_NAME = 'operations_classification'
            AND INDEX_NAME = 'operations__start_d_ccf84a_idx'
        """)
        if cursor.fetchone()[0] == 0:
            print("Ajout de l'index sur start_datetime...")
            cursor.execute("""
                CREATE INDEX operations__start_d_ccf84a_idx
                ON operations_classification (start_datetime)
            """)


class Migration(migrations.Migration):

    dependencies = [
        ('operations', '0013_fix_classification_fields'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='classification',
            name='classification_date',
        ),
        migrations.RunPython(restore_structure, reverse_code=migrations.RunPython.noop),
        migrations.AddField(
            model_name='classification',
            name='start_datetime',
            field=models.DateTimeField(blank=True, help_text='Début de la classification', null=True, verbose_name='Date et heure de début'),
        ),
    ]
