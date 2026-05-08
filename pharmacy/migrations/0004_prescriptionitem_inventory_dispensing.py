from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('pharmacy', '0003_prescription_prescription_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='prescriptionitem',
            name='inventory_item',
            field=models.ForeignKey(
                blank=True, null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='dispensed_items',
                to='pharmacy.medicationinventory',
            ),
        ),
        migrations.AddField(
            model_name='prescriptionitem',
            name='out_of_stock',
            field=models.BooleanField(default=False),
        ),
    ]
