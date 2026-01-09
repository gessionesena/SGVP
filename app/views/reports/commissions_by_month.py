from collections import defaultdict
from decimal import Decimal
from django.db.models import Sum
from django.db.models.functions import TruncMonth
from django.shortcuts import render
from installments.models import Installment
from customers.models import Customer


def commissions_by_month_report(request):
    selected_month = request.GET.get('month')

    customers = Customer.objects.all()
    installments = Installment.objects.select_related(
        'sale', 'sale__customer'
    ).filter(
        commission_value__gt=Decimal('0.00')
    )

    months = (
        installments.annotate(month=TruncMonth('due_date'))
        .values('month')
        .distinct()
        .order_by('month')
    )

    total_commission_month = Decimal('0.00')
    grouped_installments = defaultdict(lambda: {
        'items': [],
        'total_commission': Decimal('0.00'),
    })

    if selected_month:
        year, month = selected_month.split('-')
        installments = installments.filter(
            due_date__year=int(year),
            due_date__month=int(month)
        ).order_by('due_date')

        total_commission_month = installments.aggregate(
            total=Sum('commission_value')
        )['total'] or Decimal('0.00')

    else:
        installments = installments.annotate(
            month=TruncMonth('due_date')
        ).order_by('month', 'due_date')

        for installment in installments:
            grouped_installments[installment.month]['items'].append(installment)
            grouped_installments[installment.month]['total_commission'] += installment.commission_value

    context = {
        'installments': installments,
        'customers': customers,
        'grouped_installments': dict(grouped_installments),
        'selected_month': selected_month,
        'months': months,
        'total_commission_month': total_commission_month,
    }

    return render(request, 'reports/commissions_by_month.html', context)
