# Generated manually

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('operations', '0002_classification_classificationitem_and_more'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='ArrivalNote',
            new_name='Reception',
        ),
        migrations.RenameModel(
            old_name='Classification',
            new_name='Report',
        ),
        migrations.RenameModel(
            old_name='ClassificationItem',
            new_name='ReportItem',
        ),
        migrations.AlterModelTable(
            name='reception',
            table='operations_reception',
        ),
        migrations.AlterModelTable(
            name='report',
            table='operations_report',
        ),
        migrations.AlterModelTable(
            name='reportitem',
            table='operations_reportitem',
        ),
    ]
