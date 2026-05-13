from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lab_tests', '0002_labtest_walkin'),
    ]

    operations = [
        migrations.AddField(
            model_name='labtest',
            name='lab_order_ref',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
