import os
from weasyprint import HTML, CSS
from django.conf import settings
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.shortcuts import render
from sales.models import Sale
from installments.models import Installment


def installments_by_sale_report(request):
    sale_id = request.GET.get('sale')

    sales = Sale.objects.all()
    installments = Installment.objects.none()

    if sale_id:
        installments = Installment.objects.select_related(
            'sale', 'sale__customer'
        ).filter(
            sale=sale_id
        )

    context = {
        'installments': installments,
        'sales': sales,
        'selected_sale': sale_id,
    }

    if request.GET.get('pdf') == '1':
        html_string = render_to_string(
            'reports/installments_by_sale_pdf.html',
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
            'inline; filename="parcelas_por_venda.pdf"'
        )

        HTML(
            string=html_string
        ).write_pdf(response, stylesheets=[CSS(filename=css_path)])

        return response

    return render(request, 'reports/installments_by_sale.html', context)
