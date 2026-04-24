from django.db import models
from django.contrib.auth import get_user_model
import re

User = get_user_model()

CLINIC_PREFIX = 'DANNYS'


def _slugify_name(name):
    """Convert HMO name to a short uppercase slug. e.g. 'AVOH HMO' → 'AVOH'"""
    # Remove common suffixes, uppercase, keep only letters/digits
    name = re.sub(r'\bHMO\b', '', name, flags=re.IGNORECASE).strip()
    name = re.sub(r'[^A-Za-z0-9]', '', name).upper()
    return name[:10]  # max 10 chars


class HMO(models.Model):
    name = models.CharField(max_length=200, unique=True)
    code = models.CharField(max_length=50, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'hmos'
        ordering = ['name']

    def save(self, *args, **kwargs):
        # Auto-generate code if not set
        if not self.code:
            slug = _slugify_name(self.name)
            self.code = f"{CLINIC_PREFIX}-{slug}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.code})"


class Patient(models.Model):
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
        ('prefer_not_to_say', 'Prefer not to say'),
    ]

    BLOOD_TYPE_CHOICES = [
        ('A+', 'A+'), ('A-', 'A-'), ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'), ('O+', 'O+'), ('O-', 'O-'),
        ('unknown', 'Unknown'),
    ]

    PATIENT_TYPE_CHOICES = [
        ('outpatient', 'Outpatient'),
        ('retainership', 'Retainership (HMO)'),
    ]

    # Portal user link
    user = models.OneToOneField(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='patient_profile', limit_choices_to={'role': 'patient'}
    )

    # Patient code e.g. DANNYS-NHIA-0001 or DANNYS-OUT-0001
    patient_code = models.CharField(max_length=30, unique=True, blank=True, null=True)

    # Basic Information
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES)
    blood_type = models.CharField(max_length=10, choices=BLOOD_TYPE_CHOICES, blank=True, null=True)

    # Contact Information
    email = models.EmailField(unique=True, blank=True, null=True)
    phone_number = models.CharField(max_length=20)
    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    zip_code = models.CharField(max_length=20, blank=True, null=True)
    country = models.CharField(max_length=100, default='Nigeria')

    # Patient Classification
    patient_type = models.CharField(max_length=20, choices=PATIENT_TYPE_CHOICES, default='outpatient')
    hmo = models.ForeignKey(HMO, on_delete=models.SET_NULL, null=True, blank=True, related_name='patients')

    # Medical Information
    emergency_contact_name = models.CharField(max_length=200, blank=True, null=True)
    emergency_contact_phone = models.CharField(max_length=20, blank=True, null=True)
    emergency_contact_relationship = models.CharField(max_length=100, blank=True, null=True)
    allergies = models.TextField(blank=True, null=True)
    medical_conditions = models.TextField(blank=True, null=True)
    medications = models.TextField(blank=True, null=True)

    # Insurance Information
    insurance_provider = models.CharField(max_length=200, blank=True, null=True)
    insurance_policy_number = models.CharField(max_length=100, blank=True, null=True)

    # Additional Information
    notes = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    assigned_doctor = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='assigned_patients', limit_choices_to={'role': 'doctor'}
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='patients_created')

    class Meta:
        db_table = 'patients'
        verbose_name = 'Patient'
        verbose_name_plural = 'Patients'
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        regenerate = False
        if not self.pk:
            # New patient — always generate
            regenerate = True
        elif not self.patient_code:
            # Existing patient with no code yet
            regenerate = True
        else:
            # Check if HMO or patient_type changed
            try:
                old = Patient.objects.get(pk=self.pk)
                if old.hmo_id != self.hmo_id or old.patient_type != self.patient_type:
                    regenerate = True
            except Patient.DoesNotExist:
                regenerate = True

        if regenerate:
            self.patient_code = self._generate_code()
        super().save(*args, **kwargs)

    def _generate_code(self):
        if self.patient_type == 'retainership' and self.hmo:
            hmo_code = self.hmo.code or f"{CLINIC_PREFIX}-{_slugify_name(self.hmo.name)}"
            prefix = hmo_code
        else:
            prefix = f"{CLINIC_PREFIX}-OUT"

        # Find the next number that isn't already taken
        n = 1
        while True:
            code = f"{prefix}-{n:04d}"
            qs = Patient.objects.filter(patient_code=code)
            if self.pk:
                qs = qs.exclude(pk=self.pk)
            if not qs.exists():
                return code
            n += 1

    def __str__(self):
        return f"{self.full_name} [{self.patient_code}]"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    @property
    def age(self):
        from datetime import date
        today = date.today()
        return today.year - self.date_of_birth.year - (
            (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
        )
