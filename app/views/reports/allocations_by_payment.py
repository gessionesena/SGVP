from django.shortcuts import render
from payments_allocations.models import Payment_Allocation
from payments.models import Payment


def allocations_by_payment_report(request):
    payment_id = request.GET.get('payment')

    payments = Payment.objects.all()
    allocations = Payment_Allocation.objects.none()

    if payment_id:
        allocations = Payment_Allocation.objects.select_related(
            'installment', 'installment__sale', 'payment', 'payment__customer'
        ).filter(
            payment=payment_id
        )

    context = {
        'payments': payments,
        'allocations': allocations,
        'selected_payment': payment_id,
    }

    return render(request, 'reports/allocations_by_payment.html', context)
