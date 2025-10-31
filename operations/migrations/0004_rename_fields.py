# Generated manually

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('operations', '0003_rename_tables'),
    ]

    operations = [
        migrations.RenameField(
            model_name='report',
            old_name='classification_date',
            new_name='report_date',
        ),
        migrations.RenameField(
            model_name='reportitem',
            old_name='classification',
            new_name='report',
        ),
    ]
