from django.contrib import admin
from .models import Prescription, MedicationInventory

admin.site.register(Prescription)
admin.site.register(MedicationInventory)
