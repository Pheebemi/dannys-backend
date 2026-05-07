import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pharmacy', '0002_remove_prescription_dosage_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='prescription',
            name='prescription_date',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
