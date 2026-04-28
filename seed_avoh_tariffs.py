import os, django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dannys_wellness.settings")
django.setup()
from billing.models import Service, ServiceTariff
from patients.models import HMO

try:
    hmo = HMO.objects.get(name__icontains="AVOH")
    print(f"HMO: {hmo.name}")
except HMO.DoesNotExist:
    print("ERROR: AVOH HMO not found."); exit()

tariffs = [
    ("Wound Dressing", 1250.0),
    ("Wound Dressing", 2750.0),
    ("Delivery", 62150.0),
    ("Delivery", 69000.0),
    ("Delivery", 62150.0),
    ("Delivery", 50000.0),
    ("Echocardiography", 28000.0),
    ("Lipid Profile", 4000.0),
    ("Urea", 4025.0),
    ("Urinalysis", 550.0),
    ("Albumin", 1000.0),
    ("Total Bilirubin", 904.0),
    ("Occult Blood", 1250.0),
    ("Calcium", 1059.38),
    ("Cholesterol", 1380.0),
    ("Creatinine", 1059.38),
    ("Creatinine", 2000.0),
    ("HbA1C", 5000.0),
    ("Genotype", 1050.0),
    ("Magnesium", 3750.0),
    ("Urea", 1200.0),
    ("Uric Acid", 1500.0),
    ("Rheumatoid Factor", 2000.0),
    ("Blood Grouping", 706.25),
    ("Blood Giving Set", 185.0),
    ("Blood Culture", 3000.0),
    ("VDRL", 1200.0),
    ("ECG", 6000.0),
    ("ECG", 5500.0),
    ("Stool Microscopy", 1250.0),
    ("Doxycycline", 12.5),
    ("Inj. Ranitidine", 300.0),
    ("Inj. Ranitidine", 425.0),
    ("Tab Misoprostol", 225.0),
    ("Inj. Insulin", 4250.0),
    ("Inj. B. Complex", 75.0),
    ("Tab Vit E", 56.25),
    ("Tab Vit E", 37.5),
    ("Blood Tonic", 281.25),
    ("Tab Folic Acid", 5.0),
    ("Magnesium", 1225.0),
    ("Bandage", 312.5),
    ("Clotrimazole Cream", 607.0),
    ("Ketoconazole Cream", 476.25),
    ("Fluconazole", 100.0),
    ("Clotrimazole Cream", 343.75),
    ("Clotrimazole Cream", 312.5),
    ("Clotrimazole Cream", 375.0),
    ("Ketoconazole Cream", 1187.5),
    ("Calamine Lotion", 250.0),
    ("Tab Erythromycin", 37.5),
    ("Calcium", 312.5),
    ("Diclofenac 100mg", 31.25),
    ("Catheter", 250.0),
    ("Clotrimazole Cream", 850.0),
    ("Inj. Dexamethasone", 72.5),
    ("Tab Augmentin", 162.5),
    ("Tab Azithromycin 500mg", 200.0),
    ("Tab Ofloxacin", 190.0),
    ("Tab Ofloxacin", 95.0),
    ("Tab Ketoconazole", 125.0),
    ("Tab Ketoconazole", 34.0),
    ("Tab Ibuprofen 400mg", 15.0),
    ("Tab Ibuprofen 400mg", 15.0),
    ("Piroxicam", 625.0),
    ("Inj. Quinine", 125.0),
    ("Susp. Albendazole", 250.0),
    ("Susp. Albendazole", 361.25),
    ("Tab Salbutamol 4mg", 12.5),
    ("Tab Erythromycin", 25.0),
]

created = updated = 0
for name, price in tariffs:
    try:
        svc = Service.objects.get(name=name)
        _, was_created = ServiceTariff.objects.update_or_create(
            service=svc, patient_type="retainership", hmo=hmo,
            defaults={"price": price, "is_active": True}
        )
        if was_created: created += 1
        else: updated += 1
    except Service.DoesNotExist:
        print(f"  NOT FOUND: {name}")
print(f"Done! {created} created, {updated} updated.")
