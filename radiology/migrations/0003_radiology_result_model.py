import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('radiology', '0002_radiology_technical_fields'),
    ]

    operations = [
        # Remove fixed X-Ray specific fields
        migrations.RemoveField(model_name='radiologytest', name='kv'),
        migrations.RemoveField(model_name='radiologytest', name='ma'),
        migrations.RemoveField(model_name='radiologytest', name='secs'),
        migrations.RemoveField(model_name='radiologytest', name='mas'),
        migrations.RemoveField(model_name='radiologytest', name='contrast_type'),
        migrations.RemoveField(model_name='radiologytest', name='contrast_vol'),
        migrations.RemoveField(model_name='radiologytest', name='contrast_rate'),
        migrations.RemoveField(model_name='radiologytest', name='reaction'),
        migrations.RemoveField(model_name='radiologytest', name='radiographer_remarks'),
        # Add flexible result rows model
        migrations.CreateModel(
            name='RadiologyResult',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('parameter_name', models.CharField(max_length=200)),
                ('value', models.CharField(max_length=200)),
                ('unit', models.CharField(blank=True, max_length=50, null=True)),
                ('normal_range', models.CharField(blank=True, max_length=200, null=True)),
                ('is_abnormal', models.BooleanField(default=False)),
                ('notes', models.CharField(blank=True, max_length=500, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('test', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='test_results', to='radiology.radiologytest')),
            ],
            options={'db_table': 'radiology_results', 'ordering': ['id']},
        ),
    ]
