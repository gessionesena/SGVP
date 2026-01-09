from django.db.models.functions import TruncMonth
from django.shortcuts import render
from sales.models import Sale
from customers.models import Customer


def sales_by_customer_report(request):
    customer_id = request.GET.get('customer')
    selected_month = request.GET.get('month')

    customers = Customer.objects.all()
    sales = Sale.objects.none()

    if customer_id:
        sales = Sale.objects.select_related(
            'card'
        ).filter(
            customer=customer_id
        )

    months = (
        sales.annotate(month=TruncMonth('sale_date'))
        .values('month')
        .distinct()
        .order_by('-month')
    )

    if selected_month:
        year, month_number = selected_month.split('-')
        sales = sales.filter(
            sale_date__year=int(year),
            sale_date__month=int(month_number)
        ).order_by('-sale_date')

    context = {
        'customers': customers,
        'sales': sales,
        'selected_customer': customer_id,
        'selected_month': selected_month,
        'months': months,
    }

    return render(request, 'reports/sales_by_customer.html', context)
