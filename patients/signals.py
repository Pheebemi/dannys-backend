from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

User = get_user_model()


@receiver(post_save, sender=User)
def create_patient_record_for_patient_user(sender, instance, created, **kwargs):
    """
    When a User with role='patient' is saved (created or updated),
    auto-create a linked Patient record if one doesn't exist yet.
    This handles patients created directly through Django admin.
    """
    if instance.role != 'patient':
        return

    from patients.models import Patient

    # Check if a Patient record is already linked to this user
    if hasattr(instance, 'patient_profile') and instance.patient_profile is not None:
        return

    # Also check by email in case the link is missing
    if instance.email and Patient.objects.filter(email=instance.email).exists():
        existing = Patient.objects.filter(email=instance.email, user__isnull=True).first()
        if existing:
            existing.user = instance
            existing.save(update_fields=['user'])
        return

    # Create a new Patient record with the info available from the User
    # DOB is required — use a placeholder if not known
    from datetime import date
    Patient.objects.create(
        user=instance,
        first_name=instance.first_name or instance.username,
        last_name=instance.last_name or '',
        email=instance.email or None,
        phone_number=instance.phone_number or '',
        date_of_birth=date(2000, 1, 1),  # placeholder — receptionist should update
        gender='prefer_not_to_say',
        created_by=instance,
    )
