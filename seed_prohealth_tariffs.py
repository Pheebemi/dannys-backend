import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dannys_wellness.settings')
django.setup()

from billing.models import Service, ServiceTariff
from patients.models import HMO

# Get PROHEALTH HMO
try:
    hmo = HMO.objects.get(name__icontains='PROHEALTH')
    print(f"HMO: {hmo.name} ({hmo.code})")
except HMO.DoesNotExist:
    print("ERROR: PROHEALTH HMO not found. Run seed_hmos.py first.")
    exit()

# Matched tariffs: (Our Service Name, PROHEALTH Price)
tariffs = [
    ("Albumin", 800),
    ("Delivery", 12000),
    ("Blood Tonic", 1500),
    ("Blood Culture", 3600),
    ("Blood Giving Set", 270),
    ("Blood Grouping", 800),
    ("Calamine Lotion", 500),
    ("Calcium", 840),
    ("CD4 Count", 6000),
    ("Cholesterol", 1200),
    ("Creatinine", 720),
    ("Diclofenac 100mg", 75),
    ("Doxycycline", 25),
    ("Echocardiography", 24000),
    ("ECG", 6000),
    ("ESR", 750),
    ("Fluconazole", 500),
    ("Genotype", 1350),
    ("PCV", 1000),
    ("HBV", 1200),
    ("Ketoconazole Cream", 750),
    ("Lipid Profile", 4200),
    ("Total Bilirubin", 720),
    ("Magnesium", 840),
    ("HVS MCS", 1500),
    ("Stool Microscopy", 700),
    ("Occult Blood", 1200),
    ("Piroxicam", 15),
    ("Rheumatoid Factor", 18000),
    ("Syringe 2mls", 100),
    ("Urea", 720),
    ("Uric Acid", 1000),
    ("Urinalysis", 600),
    ("Urine Bag", 350),
    ("VDRL", 720),
    ("Widal", 1000),
    ("Wound Dressing", 3000),
]

created = 0
updated = 0
not_found = []

for service_name, price in tariffs:
    try:
        service = Service.objects.get(name=service_name)
        obj, was_created = ServiceTariff.objects.update_or_create(
            service=service,
            patient_type='retainership',
            hmo=hmo,
            defaults={'price': price, 'is_active': True}
        )
        if was_created:
            created += 1
            print(f"  Created: {service_name} -> {price:,}")
        else:
            updated += 1
            print(f"  Updated: {service_name} -> {price:,}")
    except Service.DoesNotExist:
        not_found.append(service_name)
        print(f"  NOT FOUND: {service_name}")

print(f"\nDone! {created} created, {updated} updated.")
if not_found:
    print(f"Services not found in DB ({len(not_found)}): {not_found}")
print(f"\nNote: {37 - len(tariffs)} services from PROHEALTH tariff had no match in our services list.")
print("Add missing services to seed_services.py first, then re-run this script.")
