# Generated manually on 2025-11-03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('operations', '0010_remove_report_operations__classif_0930be_idx_and_more'),
    ]

    operations = [
        # Rename the field from report_date to classification_date
        migrations.RenameField(
            model_name='classification',
            old_name='report_date',
            new_name='classification_date',
        ),
    ]
