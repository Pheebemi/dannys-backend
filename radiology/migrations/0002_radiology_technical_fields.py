from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('radiology', '0001_initial'),
    ]

    operations = [
        migrations.AddField(model_name='radiologytest', name='kv', field=models.CharField(blank=True, max_length=20, null=True)),
        migrations.AddField(model_name='radiologytest', name='ma', field=models.CharField(blank=True, max_length=20, null=True)),
        migrations.AddField(model_name='radiologytest', name='secs', field=models.CharField(blank=True, max_length=20, null=True)),
        migrations.AddField(model_name='radiologytest', name='mas', field=models.CharField(blank=True, max_length=20, null=True)),
        migrations.AddField(model_name='radiologytest', name='contrast_type', field=models.CharField(blank=True, max_length=100, null=True)),
        migrations.AddField(model_name='radiologytest', name='contrast_vol', field=models.CharField(blank=True, max_length=50, null=True)),
        migrations.AddField(model_name='radiologytest', name='contrast_rate', field=models.CharField(blank=True, max_length=50, null=True)),
        migrations.AddField(model_name='radiologytest', name='reaction', field=models.CharField(blank=True, choices=[('nil', 'Nil'), ('mild', 'Mild'), ('moderate', 'Moderate'), ('severe', 'Severe')], max_length=10, null=True)),
        migrations.AddField(model_name='radiologytest', name='radiographer_remarks', field=models.TextField(blank=True, null=True)),
    ]
