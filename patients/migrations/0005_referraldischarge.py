import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('patients', '0004_patient_patient_code'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ReferralDischarge',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('diagnosis', models.TextField(blank=True, null=True)),
                ('history', models.TextField(blank=True, null=True)),
                ('on_examination', models.TextField(blank=True, null=True)),
                ('course_in_hospital', models.TextField(blank=True, null=True)),
                ('advice_on_discharge', models.TextField(blank=True, null=True)),
                ('lab_scientist_name', models.CharField(blank=True, max_length=200, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='referrals', to='patients.patient')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='referrals_created', to=settings.AUTH_USER_MODEL)),
            ],
            options={'db_table': 'referral_discharges', 'ordering': ['-date', '-created_at']},
        ),
    ]
