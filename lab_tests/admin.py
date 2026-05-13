from django.contrib import admin
from .models import LabTest, LabTestCategory, LabTestResult


@admin.register(LabTestCategory)
class LabTestCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')


class LabTestResultInline(admin.TabularInline):
    model = LabTestResult
    extra = 1


@admin.register(LabTest)
class LabTestAdmin(admin.ModelAdmin):
    list_display = ('test_name', 'get_patient_display', 'status', 'priority', 'ordered_date', 'ordered_by')
    list_filter = ('status', 'priority', 'category', 'ordered_date')
    search_fields = ('test_name', 'patient__first_name', 'patient__last_name', 'walk_in_name', 'test_code')
    readonly_fields = ('ordered_date', 'created_at', 'updated_at')
    inlines = [LabTestResultInline]

    def get_patient_display(self, obj):
        if obj.patient:
            return obj.patient.full_name
        return f"Walk-in: {obj.walk_in_name or '—'}"
    get_patient_display.short_description = 'Patient'

    fieldsets = (
        ('Test Information', {
            'fields': ('test_name', 'category', 'test_code', 'description', 'instructions')
        }),
        ('Patient & Staff', {
            'fields': ('patient', 'walk_in_name', 'ordered_by', 'performed_by')
        }),
        ('Status & Priority', {
            'fields': ('status', 'priority')
        }),
        ('Dates', {
            'fields': ('ordered_date', 'scheduled_date', 'completed_date')
        }),
        ('Results', {
            'fields': ('results', 'normal_range', 'notes')
        }),
        ('Financial', {
            'fields': ('cost',)
        }),
    )


@admin.register(LabTestResult)
class LabTestResultAdmin(admin.ModelAdmin):
    list_display = ('test', 'parameter_name', 'value', 'unit', 'is_abnormal')
    list_filter = ('is_abnormal', 'test__status')
    search_fields = ('parameter_name', 'test__test_name', 'test__patient__first_name')
