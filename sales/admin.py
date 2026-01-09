from django.contrib import admin, messages
from . import models, services
from payments_allocations.models import Payment_Allocation


@admin.register(models.Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'customer',
        'category',
        'card',
        'sale_date',
        'cost_price',
        'selling_price',
        'installment_quantity',
        'description',
    )
    search_fields = (
        'title',
        'customer__name',
        'category__title',
        'card__title',
    )
    list_filter = ('sale_date',)

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

        if not change:
            services.generate_sale_installments(obj)
            return

        fields_that_trigger_recreation = [
            'selling_price',
            'installment_quantity',
            'card',
            'sale_date'
        ]

        has_relevant_change = any(field in form.changed_data for field in fields_that_trigger_recreation)

        if has_relevant_change:
            has_payments = Payment_Allocation.objects.filter(
                installment__sale=obj
            ).exists()

            if has_payments:
                messages.error(request, "Venda salva, mas parcelas NÃO atualizadas (pagamentos existentes).")
            else:
                services.generate_sale_installments(obj)
                messages.success(request, "Venda e parcelas atualizadas com sucesso.")
