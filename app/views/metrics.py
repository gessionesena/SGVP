
from calendar import monthrange
from datetime import date, timedelta
from decimal import Decimal, ROUND_HALF_UP

from dateutil.relativedelta import relativedelta
from django.db.models import Count, F, Sum
from django.db.models.functions import TruncMonth
from django.utils import timezone
from django.utils.formats import date_format, number_format

from sales.models import Sale
from installments.models import Installment
from categories.models import Category
from cards.models import Card
from customers.models import Customer
from payments_allocations.models import Payment_Allocation


ZERO = Decimal("0.00")


# ==========================================================
# FUNÇÕES AUXILIARES
# ==========================================================

def _get_sum(queryset, field):
    """Retorna a soma de um campo ou zero quando não houver valores."""
    return queryset.aggregate(total=Sum(field))["total"] or ZERO


def _format_currency(value):
    """Formata valores monetários para exibição."""
    return number_format(
        value,
        decimal_pos=2,
        force_grouping=True,
    )


def _to_float(value, quantize=False):
    """Converte Decimal para float, com arredondamento opcional."""
    if quantize:
        value = value.quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP,
        )

    return float(value)


def _get_monthly_chart_data(
    queryset,
    date_field,
    value_field,
    months_before=11,
    months_after=1,
    filters=None,
):
    """
    Gera datas e valores mensais para os gráficos.

    Por padrão, retorna 11 meses anteriores,
    o mês atual e o mês seguinte.
    """
    today = timezone.now().date().replace(day=1)

    start_date = today - relativedelta(months=months_before)
    end_date = today + relativedelta(months=months_after + 1)

    query_filters = {
        f"{date_field}__gte": start_date,
        f"{date_field}__lt": end_date,
    }

    if filters:
        query_filters.update(filters)

    monthly_data = (
        queryset
        .filter(**query_filters)
        .annotate(month=TruncMonth(date_field))
        .values("month")
        .annotate(total=Sum(value_field))
        .order_by("month")
    )

    monthly_dict = {
        item["month"]: item["total"]
        for item in monthly_data
    }

    dates = []
    values = []

    for i in range(months_before, -months_after - 1, -1):
        month = today - relativedelta(months=i)

        dates.append(date_format(month, "b/Y").title())

        total = monthly_dict.get(month, ZERO)
        values.append(_to_float(total, quantize=True))

    return {
        "dates": dates,
        "values": values,
    }


# ==========================================================
# MÉTRICAS DE VENDAS
# ==========================================================

def get_sales_metrics():
    sales = Sale.objects.aggregate(
        total_sales=Count("id"),
        total_sales_cost=Sum("cost_price"),
        total_sales_value=Sum("selling_price"),
    )

    total_sales = sales["total_sales"]
    total_sales_cost = sales["total_sales_cost"] or ZERO
    total_sales_value = sales["total_sales_value"] or ZERO

    total_sales_profit = total_sales_value - total_sales_cost

    return {
        "total_sales": total_sales,
        "total_sales_cost": _format_currency(total_sales_cost),
        "total_sales_value": _format_currency(total_sales_value),
        "total_sales_profit": _format_currency(total_sales_profit),
    }


# ==========================================================
# MÉTRICAS DE COMISSÕES
# ==========================================================

def get_commissions_metrics():
    today = date.today()
    next_month = today + relativedelta(months=1)

    current_month_filter = {
        "due_date__month": today.month,
        "due_date__year": today.year,
    }

    next_month_filter = {
        "due_date__month": next_month.month,
        "due_date__year": next_month.year,
    }

    total_commission_current_month = _get_sum(
        Installment.objects.filter(**current_month_filter),
        "commission_value",
    )

    total_commission_next_month = _get_sum(
        Installment.objects.filter(**next_month_filter),
        "commission_value",
    )

    total_commission = _get_sum(
        Installment.objects.all(),
        "commission_value",
    )

    return {
        "total_commission_current_month": _format_currency(
            total_commission_current_month
        ),
        "total_commission_next_month": _format_currency(
            total_commission_next_month
        ),
        "total_commission": _format_currency(total_commission),
    }


# ==========================================================
# VENDAS DIÁRIAS
# ==========================================================

def get_daily_sales_data():
    today = timezone.now().date()

    dates = [
        today - timedelta(days=i)
        for i in range(29, -1, -1)
    ]

    daily_sales = (
        Sale.objects
        .filter(sale_date__gte=dates[0], sale_date__lte=today)
        .values("sale_date")
        .annotate(total_sales=Sum("selling_price"))
        .order_by("sale_date")
    )

    sales_dict = {
        item["sale_date"]: item["total_sales"]
        for item in daily_sales
    }

    formatted_dates = [
        item.strftime("%d/%m/%Y")
        for item in dates
    ]

    values = [
        float(sales_dict.get(item, ZERO))
        for item in dates
    ]

    return {
        "dates": formatted_dates,
        "values": values,
    }


# ==========================================================
# VENDAS MENSAIS
# ==========================================================

def get_monthly_sales_last_12_months():
    return _get_monthly_chart_data(
        queryset=Sale.objects.all(),
        date_field="sale_date",
        value_field="selling_price",
        months_before=11,
        months_after=0,
    )


# ==========================================================
# GRÁFICOS DE VENDAS POR CATEGORIA
# ==========================================================

def get_graphic_sale_category_metric():
    categories = Category.objects.all()

    sales_by_category = (
        Sale.objects
        .values("category_id")
        .annotate(total=Count("id"))
    )

    sales_dict = {
        item["category_id"]: item["total"]
        for item in sales_by_category
    }

    return {
        category.title: sales_dict.get(category.pk, 0)
        for category in categories
    }


# ==========================================================
# GRÁFICOS DE VENDAS POR CARTÃO
# ==========================================================

def get_graphic_sale_card_metric():
    today = date.today()

    sales_by_card = (
        Sale.objects
        .filter(
            sale_date__month=today.month,
            sale_date__year=today.year,
        )
        .values("card_id")
        .annotate(total=Sum("cost_price"))
    )

    sales_dict = {
        item["card_id"]: item["total"]
        for item in sales_by_card
    }

    return {
        card.title: _to_float(sales_dict.get(card.pk) or ZERO)
        for card in Card.objects.all()
    }


# ==========================================================
# GRÁFICOS DE VENDAS POR CLIENTE
# ==========================================================

def get_graphic_sale_customer_metric():
    today = date.today()

    sales_by_customer = (
        Sale.objects
        .filter(
            sale_date__month=today.month,
            sale_date__year=today.year,
        )
        .values("customer_id")
        .annotate(total=Sum("selling_price"))
    )

    sales_dict = {
        item["customer_id"]: item["total"]
        for item in sales_by_customer
    }

    return {
        customer.name: _to_float(sales_dict.get(customer.pk) or ZERO)
        for customer in Customer.objects.all()
    }


# ==========================================================
# PRÓXIMAS PARCELAS POR CARTÃO
# ==========================================================

def get_next_due_installments_by_card():
    today = date.today()
    cards = list(Card.objects.all())

    all_installments = (
        Installment.objects
        .annotate(
            installment_value=(
                F("sale__cost_price") / F("sale__installment_quantity")
            )
        )
    )

    installments_by_card = (
        all_installments
        .values("sale__card_id", "due_date")
        .annotate(total=Sum("installment_value"))
    )

    installments_dict = {
        (item["sale__card_id"], item["due_date"]): item["total"]
        for item in installments_by_card
    }

    result = {}

    for card in cards:
        due_day = card.payment_due_day
        limit_day = max(1, due_day - 5)

        if today.day >= limit_day:
            next_month = today + relativedelta(months=1)
            year, month = next_month.year, next_month.month
        else:
            year, month = today.year, today.month

        last_day = monthrange(year, month)[1]
        final_due_day = min(due_day, last_day)

        next_due_date = date(year, month, final_due_day)

        subtotal = installments_dict.get(
            (card.pk, next_due_date),
            ZERO,
        )

        result[card.title] = _to_float(
            subtotal,
            quantize=True,
        )

    return result


# ==========================================================
# COMISSÕES MENSAIS
# ==========================================================

def get_monthly_commissions_last_12_months():
    return _get_monthly_chart_data(
        queryset=Installment.objects.all(),
        date_field="due_date",
        value_field="commission_value",
        months_before=11,
        months_after=1,
        filters={
            "commission_value__gt": ZERO,
        },
    )


# ==========================================================
# PARCELAS MENSAIS
# ==========================================================

def get_monthly_installments_last_12_months():
    return _get_monthly_chart_data(
        queryset=Installment.objects.all(),
        date_field="due_date",
        value_field="amount_total",
        months_before=11,
        months_after=1,
    )


# ==========================================================
# PAGAMENTOS MENSAIS
# ==========================================================

def get_monthly_payment_allocations_last_12_months():
    return _get_monthly_chart_data(
        queryset=Payment_Allocation.objects.all(),
        date_field="installment__due_date",
        value_field="amount_applied",
        months_before=11,
        months_after=1,
    )
