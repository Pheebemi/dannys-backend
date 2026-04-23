from django.contrib import admin
from .models import VitalSign, MedicationRecord

admin.site.register(VitalSign)
admin.site.register(MedicationRecord)
