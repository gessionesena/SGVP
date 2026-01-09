from django.contrib import admin
from . import models


@admin.register(models.Installment)
class InstallmentAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'number', 'due_date', 'amount', 'commission_value', 'late_fee_value',)
    search_fields = ('sale__title', 'sale__customer__name',)
    list_filter = ('due_date',)
    readonly_fields = ('amount_total',)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related(
            'sale',
            'sale__customer'
        )
