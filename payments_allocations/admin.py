from django.contrib import admin
from . import models


@admin.register(models.Payment_Allocation)
class Payment_AllocationAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'amount_applied', 'description',)
    search_fields = ('payment__customer__name', 'installment__sale__title',)
    list_filter = ('created_at',)
    raw_id_fields = ('payment', 'installment')

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related(
            'payment',
            'installment',
            'payment__customer',
            'installment__sale'
        )
