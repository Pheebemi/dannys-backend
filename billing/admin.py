from django.contrib import admin
from .models import Invoice, InvoiceItem, Payment, Service


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'is_active')
    list_filter = ('category', 'is_active')
    search_fields = ('name', 'description')


class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    extra = 1


class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0
    readonly_fields = ('created_at',)


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('invoice_number', 'patient', 'status', 'total_amount', 'paid_amount', 'balance', 'invoice_date')
    list_filter = ('status', 'invoice_date')
    search_fields = ('invoice_number', 'patient__first_name', 'patient__last_name')
    readonly_fields = ('invoice_number', 'created_at', 'updated_at', 'created_by')
    inlines = [InvoiceItemInline, PaymentInline]
    
    fieldsets = (
        ('Invoice Information', {
            'fields': ('invoice_number', 'patient', 'status', 'invoice_date', 'due_date')
        }),
        ('Financial', {
            'fields': ('subtotal', 'tax_rate', 'tax_amount', 'discount', 'total_amount', 'paid_amount', 'balance')
        }),
        ('Additional', {
            'fields': ('notes', 'created_by', 'created_at', 'updated_at')
        }),
    )


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('invoice', 'amount', 'payment_method', 'payment_date', 'processed_by')
    list_filter = ('payment_method', 'payment_date')
    search_fields = ('invoice__invoice_number', 'reference_number')
    readonly_fields = ('created_at',)

