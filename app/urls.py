from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include
from app.views.home import home
from app.views.reports_menu import reports_menu
from app.views.reports import overdue_installments, sales_by_customer, sales_by_card, sales_by_category, installments_by_sale, installments_by_customer, installments_by_card, payments_by_customer, allocations_by_payment, allocations_by_installment, installments_by_due_date, commissions_by_month


urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    path('', home, name='home'),
    path('reports/', reports_menu, name='reports_menu'),

    path("reports/sales_by_customer/", sales_by_customer.sales_by_customer_report, name="sales_by_customer_report"),
    path("reports/sales_by_card/", sales_by_card.sales_by_card_report, name="sales_by_card_report"),
    path("reports/sales_by_category/", sales_by_category.sales_by_category_report, name="sales_by_category_report"),
    path("reports/installments_by_sale/", installments_by_sale.installments_by_sale_report, name="installments_by_sale_report"),
    path("reports/installments_by_customer/", installments_by_customer.installments_by_customer_report, name="installments_by_customer_report"),
    path("reports/installments_by_card/", installments_by_card.installments_by_card_report, name="installments_by_card_report"),
    path("reports/installments_by_due_date/", installments_by_due_date.installments_by_due_date_report, name="installments_by_due_date_report"),

    path("reports/payments_by_customer/", payments_by_customer.payments_by_customer_report, name="payments_by_customer_report"),
    path("reports/allocations_by_payment/", allocations_by_payment.allocations_by_payment_report, name="allocations_by_payment_report"),
    path("reports/allocations_by_installment/", allocations_by_installment.allocations_by_installment_report, name="allocations_by_installment_report"),
    path("reports/overdue_installments/", overdue_installments.overdue_installments_report, name="overdue_installments_report"),
    path("reports/commissions_by_month/", commissions_by_month.commissions_by_month_report, name="commissions_by_month_report"),

    path('', include('cards.urls')),
    path('', include('categories.urls')),
    path('', include('customers.urls')),
    path('', include('sales.urls')),
    path('', include('installments.urls')),
    path('', include('payments.urls')),
    path('', include('payments_allocations.urls')),
]
