import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('patients', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='RadiologyCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('description', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={'db_table': 'radiology_categories', 'ordering': ['name']},
        ),
        migrations.CreateModel(
            name='RadiologyTest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('test_name', models.CharField(max_length=200)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('in_progress', 'In Progress'), ('completed', 'Completed'), ('cancelled', 'Cancelled')], default='pending', max_length=20)),
                ('priority', models.CharField(choices=[('routine', 'Routine'), ('urgent', 'Urgent'), ('stat', 'STAT (Immediate)')], default='routine', max_length=10)),
                ('description', models.TextField(blank=True, null=True)),
                ('instructions', models.TextField(blank=True, null=True)),
                ('findings', models.TextField(blank=True, null=True)),
                ('impression', models.TextField(blank=True, null=True)),
                ('notes', models.TextField(blank=True, null=True)),
                ('cost', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('ordered_date', models.DateField(blank=True, null=True)),
                ('scheduled_date', models.DateTimeField(blank=True, null=True)),
                ('completed_date', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='radiology_tests', to='patients.patient')),
                ('category', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='tests', to='radiology.radiologycategory')),
                ('ordered_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='radiology_orders', to=settings.AUTH_USER_MODEL)),
                ('performed_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='radiology_performed', to=settings.AUTH_USER_MODEL)),
            ],
            options={'db_table': 'radiology_tests', 'ordering': ['-created_at']},
        ),
    ]
