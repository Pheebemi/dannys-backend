from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('lab_tests', '0001_initial'),
        ('patients', '0005_referraldischarge'),
    ]

    operations = [
        migrations.AddField(
            model_name='labtest',
            name='walk_in_name',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='labtest',
            name='patient',
            field=models.ForeignKey(
                blank=True, null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='lab_tests',
                to='patients.patient',
            ),
        ),
    ]
