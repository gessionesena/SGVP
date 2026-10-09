
import os
from collections import defaultdict
from decimal import Decimal

from django.conf import settings
from django.db.models import (
    Sum,
    F,
    Value,
    ExpressionWrapper,
    DecimalField,
)
from django.db.models.functions import Coalesce
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.utils.timezone import now
from weasyprint import HTML, CSS

from installments.models import Installment


def all_open_installments_report(request):
    installments = (
        Installment.objects
        .select_related('sale', 'sale__customer')
        .annotate(
            total_paid=Coalesce(
                Sum('payments_allocations__amount_applied'),
                Value(
                    Decimal('0.00'),
                    output_field=DecimalField(
                        max_digits=12,
                        decimal_places=2,
                    ),
                ),
            ),
        )
        .annotate(
            remaining_balance=ExpressionWrapper(
                F('amount_total') - F('total_paid'),
                output_field=DecimalField(
                    max_digits=12,
                    decimal_places=2,
                ),
            )
        )
        .filter(
            remaining_balance__gt=Decimal('0.01')
        )
        .order_by(
            'sale__customer__name',
            'due_date',
            'sale_id',
            'number',
        )
    )

    grouped_customers = defaultdict(
        lambda: {
            'customer': None,
            'items': [],
            'total_amount': Decimal('0.00'),
            'total_balance': Decimal('0.00'),
        }
    )

    total_amount = Decimal('0.00')
    total_balance = Decimal('0.00')

    for installment in installments:
        customer = installment.sale.customer

        group = grouped_customers[customer.pk]
        group['customer'] = customer
        group['items'].append(installment)

        group['total_amount'] += installment.amount_total
        group['total_balance'] += installment.remaining_balance

        total_amount += installment.amount_total
        total_balance += installment.remaining_balance

    context = {
        'grouped_customers': list(grouped_customers.values()),
        'total_customers': len(grouped_customers),
        'total_installments': sum(
            len(group['items'])
            for group in grouped_customers.values()
        ),
        'total_amount': total_amount,
        'total_balance': total_balance,
        'generated_at': now(),
    }

    html_string = render_to_string(
        'reports/all_open_installments_pdf.html',
        context,
    )

    css_path = os.path.join(
        settings.BASE_DIR,
        'app',
        'static',
        'reports',
        'reports.css',
    )

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = (
        'attachment; filename="backup_parcelas_em_aberto.pdf"'
    )

    HTML(string=html_string).write_pdf(
        response,
        stylesheets=[CSS(filename=css_path)],
    )

    return response