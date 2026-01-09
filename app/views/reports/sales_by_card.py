from django.db.models.functions import TruncMonth
from django.shortcuts import render
from sales.models import Sale
from cards.models import Card


def sales_by_card_report(request):
    card_id = request.GET.get('card')
    selected_month = request.GET.get('month')

    cards = Card.objects.all()
    sales = Sale.objects.none()

    if card_id:
        sales = Sale.objects.select_related(
            'card', 'customer'
        ).filter(
            card=card_id
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
        'cards': cards,
        'sales': sales,
        'selected_card': card_id,
        'selected_month': selected_month,
        'months': months,
    }

    return render(request, 'reports/sales_by_card.html', context)
