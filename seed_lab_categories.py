import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dannys_wellness.settings')
django.setup()

from lab_tests.models import LabTestCategory

categories = [
    "Haematology",
    "Microbiology",
    "Serology",
    "Chemistry",
    "Immunology",
    "Parasitology",
    "Urinalysis",
    "Histopathology",
    "Molecular Biology",
    "Blood Bank",
]

created = 0
updated = 0
for name in categories:
    obj, was_created = LabTestCategory.objects.update_or_create(
        name=name,
        defaults={"is_active": True}
    )
    if was_created:
        created += 1
        print(f"  Created: {name}")
    else:
        updated += 1
        print(f"  Exists:  {name}")

print(f"\nDone! {created} created, {updated} already existed. Total: {created + updated} categories.")
