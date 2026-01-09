from calendar import monthrange
from dateutil.relativedelta import relativedelta
from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from django.utils import timezone
from django.utils.formats import number_format
from django.db.models import Sum, F
from sales.models import Sale
from installments.models import Installment
from categories.models import Category
from cards.models import Card
from customers.models import Customer


def get_sales_metrics():
    total_sales = Sale.objects.count()
    total_sales_cost = Sale.objects.aggregate(
        total=Sum('cost_price')
    )['total'] or Decimal('0.00')

    total_sales_value = Sale.objects.aggregate(
        total=Sum('selling_price')
    )['total'] or Decimal('0.00')
    total_sales_profit = total_sales_value - total_sales_cost

    return dict(
        total_sales=total_sales,
        total_sales_cost=number_format(total_sales_cost, decimal_pos=2, force_grouping=True),
        total_sales_value=number_format(total_sales_value, decimal_pos=2, force_grouping=True),
        total_sales_profit=number_format(total_sales_profit, decimal_pos=2, force_grouping=True),
    )


def get_commissions_metrics():
    today = date.today()
    next_month = today + relativedelta(months=1)

    total_commission_current_month = Installment.objects.filter(
        due_date__month=today.month,
        due_date__year=today.year
    ).aggregate(
        total=Sum('commission_value')
    )['total'] or Decimal('0.00')

    total_commission_next_month = Installment.objects.filter(
        due_date__month=next_month.month,
        due_date__year=next_month.year,
    ).aggregate(
        total=Sum('commission_value')
    )['total'] or Decimal('0.00')

    total_commission = Installment.objects.aggregate(
        total=Sum('commission_value')
    )['total'] or Decimal('0.00')

    return dict(
        total_commission_current_month=number_format(total_commission_current_month, decimal_pos=2, force_grouping=True),
        total_commission_next_month=number_format(total_commission_next_month, decimal_pos=2, force_grouping=True),
        total_commission=number_format(total_commission, decimal_pos=2, force_grouping=True),
    )


def get_daily_sales_data():
    today = timezone.now().date()
    values = []
    dates = [(today - timezone.timedelta(days=i)) for i in range(29, -1, -1)]

    for item in dates:
        sales_total = Sale.objects.filter(
            sale_date=item,
        ).aggregate(
            total_sales=Sum('selling_price')
        )['total_sales'] or Decimal('0.00')

        values.append(float(sales_total))

    formatted_dates = [d.strftime("%d/%m/%Y") for d in dates]

    return dict(
        dates=formatted_dates,
        values=values,
    )


def get_monthly_sales_last_12_months():
    today = timezone.now().date().replace(day=1)

    dates = []
    values = []

    for i in range(11, -1, -1):
        month = today - relativedelta(months=i)
        month_start = month
        month_end = month + relativedelta(months=1)

        dates.append(month.strftime("%b/%y").title())

        total = (
            Sale.objects.filter(
                sale_date__gte=month_start,
                sale_date__lt=month_end
            ).aggregate(
                total_sales=Sum("selling_price")
            )["total_sales"] or Decimal('0.00')
        )
        total = total.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        values.append(float(total))

    return {"dates": dates, "values": values}


def get_graphic_sale_category_metric():
    categories = Category.objects.all()
    return {category.title: Sale.objects.filter(category=category).count() for category in categories}


def get_graphic_sale_card_metric():
    today = date.today()
    cards = Card.objects.all()

    return {card.title: float(Sale.objects.filter(
        card=card,
        sale_date__month=today.month,
        sale_date__year=today.year
    ).aggregate(
        total=Sum('cost_price')
    )['total'] or Decimal('0.00')) for card in cards}


def get_graphic_sale_customer_metric():
    today = date.today()
    customers = Customer.objects.all()

    return {customer.name: float(Sale.objects.filter(
        customer=customer,
        sale_date__month=today.month,
        sale_date__year=today.year
    ).aggregate(
        total=Sum('selling_price')
    )['total'] or Decimal('0.00')) for customer in customers}


def get_next_due_installments_by_card():
    today = date.today()
    cards = list(Card.objects.all())
    result = {}

    all_installments = (
        Installment.objects.annotate(
            installment_value=F('sale__cost_price') / F('sale__installment_quantity')
        ).select_related('sale__card')
    )

    for card in cards:
        due_day = card.payment_due_day
        limit_day = max(1, due_day - 5)

        if today.day >= limit_day:
            if today.month == 12:
                year, month = today.year + 1, 1
            else:
                year, month = today.year, today.month + 1
        else:
            year, month = today.year, today.month

        last_day = monthrange(year, month)[1]
        final_due_day = min(due_day, last_day)

        next_due_date = date(year, month, final_due_day)

        subtotal = (
            all_installments.filter(
                sale__card=card,
                due_date=next_due_date
            ).aggregate(
                total=Sum('installment_value')
            )['total'] or Decimal('0.00')
        )
        subtotal = subtotal.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        result[card.title] = float(subtotal)
    return result
