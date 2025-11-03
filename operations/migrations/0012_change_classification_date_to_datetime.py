# Generated manually on 2025-11-03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('operations', '0011_rename_report_date_to_classification_date'),
    ]

    operations = [
        # Supprimer l'index sur start_datetime
        migrations.RemoveIndex(
            model_name='classification',
            name='operations__start_d_ccf84a_idx',
        ),
        # Supprimer le champ start_datetime
        migrations.RemoveField(
            model_name='classification',
            name='start_datetime',
        ),
        # Changer classification_date de DateField à DateTimeField
        migrations.AlterField(
            model_name='classification',
            name='classification_date',
            field=models.DateTimeField(help_text='Date et heure de début du classement', verbose_name='Date et heure de classement (début)'),
        ),
    ]
