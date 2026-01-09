from django.shortcuts import render
from installments.models import Installment


def installments_by_due_date_report(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    installments = Installment.objects.select_related(
        'sale', 'sale__customer', 'sale__card'
    ).order_by('sale__card')

    if start_date:
        installments = installments.filter(due_date__gte=start_date)
    if end_date:
        installments = installments.filter(due_date__lte=end_date)

    context = {
        'installments': installments,
        'start_date': start_date,
        'end_date': end_date
    }

    return render(request, 'reports/installments_by_due_date.html', context)
