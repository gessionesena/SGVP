from django.contrib import admin
from . import models


@admin.register(models.Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('customer', 'value', 'payment_date', 'method', 'description',)
    search_fields = ('customer__name', 'value',)
    list_filter = ('payment_date',)

    def has_change_permission(self, request, obj=None):
        if obj and obj.payments_allocations.exists():
            return False
        return super().has_change_permission(request, obj)
