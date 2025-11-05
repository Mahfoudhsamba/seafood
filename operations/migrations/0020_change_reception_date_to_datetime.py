# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('operations', '0019_rename_cartonage_to_packaging'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reception',
            name='reception_date',
            field=models.DateTimeField(verbose_name='Date et heure de réception'),
        ),
    ]
