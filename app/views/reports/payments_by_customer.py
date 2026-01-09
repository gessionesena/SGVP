from django.db.models.functions import TruncMonth
from django.shortcuts import render
from customers.models import Customer
from payments.models import Payment


def payments_by_customer_report(request):
    customer_id = request.GET.get('customer')
    selected_month = request.GET.get('month')

    customers = Customer.objects.all()
    payments = Payment.objects.none()

    if customer_id:
        payments = Payment.objects.filter(
            customer=customer_id
        )

    months = (
        payments.annotate(month=TruncMonth('payment_date'))
        .values('month')
        .distinct()
        .order_by('month')
    )

    if selected_month:
        year, month_number = selected_month.split('-')
        payments = payments.filter(
            payment_date__year=int(year),
            payment_date__month=int(month_number)
        ).order_by('-payment_date')

    context = {
        'payments': payments,
        'customers': customers,
        'selected_customer': customer_id,
        'selected_month': selected_month,
        'months': months,
    }

    return render(request, 'reports/payments_by_customer.html', context)
