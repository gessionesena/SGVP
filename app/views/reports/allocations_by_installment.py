from django.shortcuts import render
from payments_allocations.models import Payment_Allocation
from installments.models import Installment


def allocations_by_installment_report(request):
    installment_id = request.GET.get('installment')

    installments = Installment.objects.all()
    allocations = Payment_Allocation.objects.none()

    if installment_id:
        allocations = Payment_Allocation.objects.select_related(
            'installment', 'installment__sale', 'installment__sale__customer'
        ).filter(
            installment=installment_id
        )

    context = {
        'installments': installments,
        'allocations': allocations,
        'selected_installment': installment_id,
    }

    return render(request, 'reports/allocations_by_installment.html', context)
