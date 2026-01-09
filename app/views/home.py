import json
import locale
from datetime import date
from dateutil.relativedelta import relativedelta
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from app.views import metrics


@login_required(login_url='login')
def home(request):
    sales_metrics = metrics.get_sales_metrics()
    commissions_metrics = metrics.get_commissions_metrics()

    today = date.today()

    MESES_PT = [
    "", "Jan", "Fev", "Mar", "Abr", "Mai", "Jun",
    "Jul", "Ago", "Set", "Out", "Nov", "Dez"
    ]

    current_month_name = MESES_PT[today.month]
    next_month_date = today + relativedelta(months=1)
    next_month_name = MESES_PT[next_month_date.month]

    daily_sales_data = metrics.get_daily_sales_data()
    monthly_sales_last_12_months = metrics.get_monthly_sales_last_12_months()
    sale_count_by_category = metrics.get_graphic_sale_category_metric()
    sale_value_current_month_by_card = metrics.get_graphic_sale_card_metric()

    sale_value_current_month_by_customer = metrics.get_graphic_sale_customer_metric()
    installment_next_due_by_card = metrics.get_next_due_installments_by_card()

    context = {
        'sales_metrics': sales_metrics,
        'commissions_metrics': commissions_metrics,
        'current_month_name': current_month_name,
        'next_month_name': next_month_name,
        'daily_sales_data': json.dumps(daily_sales_data),
        'monthly_sales_last_12_months': json.dumps(monthly_sales_last_12_months),
        'sale_count_by_category': json.dumps(sale_count_by_category),
        'sale_value_current_month_by_card': json.dumps(sale_value_current_month_by_card),
        'sale_value_current_month_by_customer': json.dumps(sale_value_current_month_by_customer),
        'installment_next_due_by_card': json.dumps(installment_next_due_by_card),
    }
    return render(request, 'home.html', context)
