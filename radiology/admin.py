from django.contrib import admin
from .models import RadiologyCategory, RadiologyTest


@admin.register(RadiologyCategory)
class RadiologyCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'created_at')
    search_fields = ('name',)


@admin.register(RadiologyTest)
class RadiologyTestAdmin(admin.ModelAdmin):
    list_display = ('test_name', 'patient', 'category', 'status', 'priority', 'ordered_by', 'performed_by', 'ordered_date', 'created_at')
    list_filter = ('status', 'priority', 'category')
    search_fields = ('test_name', 'patient__first_name', 'patient__last_name')
    readonly_fields = ('created_at', 'updated_at')
    raw_id_fields = ('patient', 'ordered_by', 'performed_by')
    fieldsets = (
        ('Test Info', {
            'fields': ('patient', 'category', 'test_name', 'status', 'priority', 'cost')
        }),
        ('Order Details', {
            'fields': ('ordered_by', 'ordered_date', 'performed_by', 'scheduled_date', 'completed_date')
        }),
        ('Clinical Notes', {
            'fields': ('description', 'instructions', 'notes')
        }),
        ('Results', {
            'fields': ('findings', 'impression'),
            'classes': ('wide',),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
