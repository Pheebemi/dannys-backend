import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dannys_wellness.settings')
django.setup()

from lab_tests.models import LabTestCategory

categories = [
    "MP (Malaria Parasite)",
    "Widal",
    "PCV",
    "Urinalysis",
    "PT (Pregnancy Test)",
    "HCV",
    "HBV",
    "ARC/RVS",
    "FBC (Full Blood Count)",
    "ESR",
    "Blood Grouping",
    "RBS (Random Blood Sugar)",
    "FBS (Fasting Blood Sugar)",
    "2HPP",
    "Urine M/C/S",
    "Stool M/C/S",
    "Stool Microscopy",
    "Occult Blood",
    "HVS MCS",
    "HbA1C",
    "AFP",
    "Lipid Profile",
    "Genotype",
    "PSA Qualitative",
    "PSA Quantitative",
    "Rheumatoid Factor",
    "H. Pylori",
    "Urea",
    "Creatinine",
    "Cholesterol",
    "Uric Acid",
    "Calcium",
    "ASL",
    "ALT",
    "LFT (Liver Function Test)",
    "E/U/CR",
    "Electrolyte",
    "Albumin",
    "HBV Quantification",
    "HBV (DNA)",
    "HCV RNA",
    "BCV Genotype",
    "Viral Screening (Donor Screening)",
    "T3 T4 and TSA",
    "HB Serology/Profile",
    "Total Bilirubin",
    "Plural Fluid AFB",
    "RFT/E/U/Cr",
    "VDRL",
    "ARC Viral Load (RNA)",
    "Asetic Fluid Analysis (AFAB)",
    "AFAC",
    "AFA Haem",
    "A Feto Protein Quantitative",
    "Magnesium",
    "Organic Phosphate",
    "Viral Maker",
    "Rheumatoid Factor +VE",
    "Blood Culture",
    "CD4 Count",
]

created = 0
existing = 0
for name in categories:
    obj, was_created = LabTestCategory.objects.update_or_create(
        name=name,
        defaults={"is_active": True}
    )
    if was_created:
        created += 1
        print(f"  Created: {name}")
    else:
        existing += 1
        print(f"  Exists:  {name}")

print(f"\nDone! {created} created, {existing} already existed. Total: {created + existing} categories.")
