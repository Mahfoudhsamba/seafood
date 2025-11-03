# Generated manually on 2025-11-03
# Migration de correction pour synchroniser la base de données avec le modèle

from django.db import migrations


def fix_classification_table(apps, schema_editor):
    """
    Migration de correction pour :
    1. Ajouter classification_date (datetime) si elle n'existe pas
    2. Copier les données de report_date vers classification_date
    3. Supprimer report_date et start_datetime
    """
    with schema_editor.connection.cursor() as cursor:
        # Vérifier si classification_date existe déjà
        cursor.execute("""
            SELECT COUNT(*)
            FROM information_schema.COLUMNS
            WHERE TABLE_SCHEMA = DATABASE()
            AND TABLE_NAME = 'operations_classification'
            AND COLUMN_NAME = 'classification_date'
        """)
        classification_date_exists = cursor.fetchone()[0] > 0

        if not classification_date_exists:
            # Ajouter la colonne classification_date comme datetime
            print("Ajout de la colonne classification_date...")
            cursor.execute("""
                ALTER TABLE operations_classification
                ADD COLUMN classification_date datetime(6) NULL AFTER reception_id
            """)

            # Copier les données de report_date vers classification_date (en ajoutant l'heure 00:00:00)
            print("Copie des données de report_date vers classification_date...")
            cursor.execute("""
                UPDATE operations_classification
                SET classification_date = CAST(CONCAT(report_date, ' 00:00:00') AS DATETIME(6))
                WHERE report_date IS NOT NULL
            """)

            # Rendre classification_date NOT NULL maintenant que les données sont copiées
            cursor.execute("""
                ALTER TABLE operations_classification
                MODIFY classification_date datetime(6) NOT NULL
            """)

        # Vérifier si report_date existe
        cursor.execute("""
            SELECT COUNT(*)
            FROM information_schema.COLUMNS
            WHERE TABLE_SCHEMA = DATABASE()
            AND TABLE_NAME = 'operations_classification'
            AND COLUMN_NAME = 'report_date'
        """)
        report_date_exists = cursor.fetchone()[0] > 0

        if report_date_exists:
            # Supprimer l'index sur report_date s'il existe
            print("Suppression de l'index sur report_date...")
            cursor.execute("""
                SELECT COUNT(*)
                FROM information_schema.STATISTICS
                WHERE TABLE_SCHEMA = DATABASE()
                AND TABLE_NAME = 'operations_classification'
                AND INDEX_NAME = 'operations__report__39e737_idx'
            """)
            if cursor.fetchone()[0] > 0:
                cursor.execute("DROP INDEX operations__report__39e737_idx ON operations_classification")

            # Supprimer la colonne report_date
            print("Suppression de la colonne report_date...")
            cursor.execute("ALTER TABLE operations_classification DROP COLUMN report_date")

        # Vérifier si start_datetime existe
        cursor.execute("""
            SELECT COUNT(*)
            FROM information_schema.COLUMNS
            WHERE TABLE_SCHEMA = DATABASE()
            AND TABLE_NAME = 'operations_classification'
            AND COLUMN_NAME = 'start_datetime'
        """)
        start_datetime_exists = cursor.fetchone()[0] > 0

        if start_datetime_exists:
            # Supprimer l'index sur start_datetime s'il existe
            print("Suppression de l'index sur start_datetime...")
            cursor.execute("""
                SELECT COUNT(*)
                FROM information_schema.STATISTICS
                WHERE TABLE_SCHEMA = DATABASE()
                AND TABLE_NAME = 'operations_classification'
                AND INDEX_NAME = 'operations__start_d_ccf84a_idx'
            """)
            if cursor.fetchone()[0] > 0:
                cursor.execute("DROP INDEX operations__start_d_ccf84a_idx ON operations_classification")

            # Supprimer la colonne start_datetime
            print("Suppression de la colonne start_datetime...")
            cursor.execute("ALTER TABLE operations_classification DROP COLUMN start_datetime")

        # Ajouter l'index sur classification_date s'il n'existe pas
        cursor.execute("""
            SELECT COUNT(*)
            FROM information_schema.STATISTICS
            WHERE TABLE_SCHEMA = DATABASE()
            AND TABLE_NAME = 'operations_classification'
            AND INDEX_NAME = 'operations__classif_date_idx'
        """)
        if cursor.fetchone()[0] == 0:
            print("Ajout de l'index sur classification_date...")
            cursor.execute("""
                CREATE INDEX operations__classif_date_idx
                ON operations_classification (classification_date)
            """)


class Migration(migrations.Migration):

    dependencies = [
        ('operations', '0012_change_classification_date_to_datetime'),
    ]

    operations = [
        migrations.RunPython(fix_classification_table, reverse_code=migrations.RunPython.noop),
    ]
