import os
from collections import defaultdict
from datetime import date
from decimal import Decimal
from weasyprint import HTML, CSS
from django.conf import settings
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.db.models.functions import TruncMonth
from django.shortcuts import render
from cards.models import Card
from installments.models import Installment


def installments_by_card_report(request):
    card_id = request.GET.get('card')
    selected_month = request.GET.get('month')

    selected_month_date = None
    if selected_month:
        year, month = selected_month.split('-')
        selected_month_date = date(int(year), int(month), 1)

    cards = Card.objects.all()
    installments = Installment.objects.none()

    if card_id:
        installments = Installment.objects.select_related(
            'sale',
            'sale__card',
            'sale__customer'
        ).filter(
            sale__card=card_id
        )

    months = (
        installments.annotate(month=TruncMonth('due_date'))
        .values('month')
        .distinct()
        .order_by('month')
    )

    total_amount_month = Decimal('0.00')
    grouped_installments = defaultdict(lambda: {
        'items': [],
        'total': 0
    })

    if selected_month:
        year, month_number = selected_month.split('-')
        installments = installments.filter(
            due_date__year=int(year),
            due_date__month=int(month_number)
        ).order_by('due_date')

        for inst in installments:
            total_amount_month += inst.amount_total

    else:
        installments = installments.annotate(
            month=TruncMonth('due_date')
        ).order_by('month', 'due_date')

        for installment in installments:
            grouped_installments[installment.month]['items'].append(installment)
            grouped_installments[installment.month]['total'] += installment.amount_total

    context = {
        'installments': installments,
        'cards': cards,
        'grouped_installments': dict(grouped_installments),
        'selected_card': card_id,
        'selected_month': selected_month,
        'selected_month_date': selected_month_date,
        'months': months,
        'total_amount_month': total_amount_month
    }

    if request.GET.get('pdf') == '1':
        html_string = render_to_string(
            'reports/installments_by_card_pdf.html',
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
            'inline; filename="parcelas_por_cartao.pdf"'
        )

        HTML(
            string=html_string
        ).write_pdf(response, stylesheets=[CSS(filename=css_path)])
        return response

    return render(request, 'reports/installments_by_card.html', context)
