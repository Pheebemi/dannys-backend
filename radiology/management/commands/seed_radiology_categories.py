from django.core.management.base import BaseCommand
from radiology.models import RadiologyCategory


CATEGORIES = [
    ("X-Ray (Plain Radiography)", "Standard X-ray imaging for bones, chest, and general anatomy"),
    ("Ultrasound (Sonography)", "Sound wave imaging for abdomen, pelvis, obstetrics, and soft tissues"),
    ("CT Scan (Computed Tomography)", "Cross-sectional imaging for detailed organ and tissue evaluation"),
    ("MRI (Magnetic Resonance Imaging)", "High-resolution imaging of soft tissues, brain, spine, and joints"),
    ("Echocardiography", "Ultrasound imaging of the heart structure and function"),
    ("Colour Doppler", "Blood flow assessment using Doppler ultrasound"),
    ("Mammography", "Breast imaging for screening and diagnosis"),
    ("Fluoroscopy", "Real-time X-ray imaging for dynamic studies (e.g. barium swallow)"),
    ("Nuclear Medicine / Scintigraphy", "Radiotracer-based imaging for organ function studies"),
    ("DEXA Scan (Bone Densitometry)", "Bone mineral density measurement for osteoporosis"),
    ("Interventional Radiology", "Image-guided procedures such as biopsies and drains"),
    ("Angiography", "Imaging of blood vessels using contrast agents"),
]


class Command(BaseCommand):
    help = "Seed default radiology categories"

    def handle(self, *args, **kwargs):
        created = 0
        skipped = 0
        for name, description in CATEGORIES:
            obj, was_created = RadiologyCategory.objects.get_or_create(
                name=name,
                defaults={"description": description},
            )
            if was_created:
                created += 1
                self.stdout.write(self.style.SUCCESS(f"  Created: {name}"))
            else:
                skipped += 1
                self.stdout.write(f"  Skipped (already exists): {name}")

        self.stdout.write(self.style.SUCCESS(
            f"\nDone — {created} created, {skipped} already existed."
        ))
