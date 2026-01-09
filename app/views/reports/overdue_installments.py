from django.db.models import Sum, F, ExpressionWrapper, DecimalField
from django.db.models.functions import Coalesce
from django.shortcuts import render
from django.utils.timezone import now
from decimal import Decimal
from installments.models import Installment


def overdue_installments_report(request):
    today = now().date()

    installments = Installment.objects.select_related(
        'sale', 'sale__customer', 'sale__card'
    ).annotate(
        total_paid=Coalesce(
            Sum('payments_allocations__amount_applied'),
            Decimal('0.00')
        ),
        remaining_balance=ExpressionWrapper(
            F('amount_total') - F('total_paid'),
            output_field=DecimalField(max_digits=10, decimal_places=2)
        )
    ).filter(
        due_date__lt=today,
        amount_total__gt=0,
        remaining_balance__gt=Decimal('0.00')
    ).order_by('due_date')

    context = {
        'installments': installments,
        'today': today,
    }

    return render(request, 'reports/overdue_installments.html', context)
