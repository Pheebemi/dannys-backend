from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nurse_care', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vitalsign',
            name='recorded_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
