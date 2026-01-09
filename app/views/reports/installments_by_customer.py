import os
from collections import defaultdict
from decimal import Decimal
from datetime import date
from weasyprint import HTML, CSS
from django.conf import settings
from django.utils.timezone import now
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.db.models import Sum, F, ExpressionWrapper, DecimalField
from django.db.models.functions import Coalesce
from django.db.models.functions import TruncMonth
from django.shortcuts import render
from customers.models import Customer
from installments.models import Installment


def installments_by_customer_report(request):
    customer_id = request.GET.get('customer')
    selected_month = request.GET.get('month')
    selected_ids = request.GET.getlist('installment_ids')

    selected_month_date = None
    if selected_month:
        year, month = selected_month.split('-')
        selected_month_date = date(int(year), int(month), 1)

    customers = Customer.objects.all()
    installments = Installment.objects.none()

    if customer_id:
        installments = Installment.objects.select_related(
            'sale', 'sale__customer'
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
            sale__customer=customer_id,
            remaining_balance__gt=Decimal('0.01')
        )

    months = (
        installments.annotate(month=TruncMonth('due_date'))
        .values('month')
        .distinct()
        .order_by('month')
    )

    total_amount_month = Decimal('0.00')
    total_balance_month = Decimal('0.00')
    grouped_installments = defaultdict(lambda: {
        'items': [],
        'total_amount': Decimal('0.00'),
        'total_balance': Decimal('0.00')
    })

    if selected_month:
        year, month_number = selected_month.split('-')
        installments = installments.filter(
            due_date__year=int(year),
            due_date__month=int(month_number)
        ).order_by('due_date')

        if request.GET.get('pdf') == '1':
            if not selected_ids:
                return render(
                    request,
                    'reports/installments_by_customer.html',
                    {
                        **locals(),
                        'error': 'Selecione ao menos uma parcela para gerar o PDF.'
                    }
                )

            installments = installments.filter(id__in=selected_ids)

        for inst in installments:
            total_amount_month += inst.amount_total
            total_balance_month += inst.remaining_balance

    else:
        installments = installments.annotate(
            month=TruncMonth('due_date')
        ).order_by('month', 'due_date')

        for installment in installments:
            grouped_installments[installment.month]['items'].append(installment)
            grouped_installments[installment.month]['total_amount'] += installment.amount_total
            grouped_installments[installment.month]['total_balance'] += installment.remaining_balance

    generated_at = now()

    context = {
        'installments': installments,
        'customers': customers,
        'grouped_installments': dict(grouped_installments),
        'selected_customer': customer_id,
        'selected_month': selected_month,
        'selected_month_date': selected_month_date,
        'months': months,
        'total_amount_month': total_amount_month,
        'total_balance_month': total_balance_month,
        'generated_at': generated_at,
    }

    if request.GET.get('pdf') == '1':
        html_string = render_to_string(
            'reports/installments_by_customer_pdf.html',
            context
        )

        css_path = os.path.join(
            settings.BASE_DIR,
            'app',
            'static',
            'reports',
            'reports.css'
        )

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = (
            'inline; filename="parcelas_em_aberto_cliente.pdf"'
        )

        HTML(string=html_string).write_pdf(
            response,
            stylesheets=[CSS(filename=css_path)]
        )

        return response

    return render(request, 'reports/installments_by_customer.html', context)
