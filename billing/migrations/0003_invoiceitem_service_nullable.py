from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('billing', '0002_servicetariff'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invoiceitem',
            name='service',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to='billing.service',
            ),
        ),
    ]
