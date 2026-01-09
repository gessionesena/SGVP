from django.urls import path
from . import views


urlpatterns = [
    path('payments_allocations/list/', views.PaymentAllocationListView.as_view(), name='payment_allocation_list'),
    path('payments_allocations/create/payment/<int:payment_id>/', views.PaymentAllocationCreateView.as_view(), name='payment_allocation_create_by_payment'),
    path('payments_allocations/create/installment/<int:installment_id>/', views.PaymentAllocationCreateView.as_view(), name='payment_allocation_create_by_installment'),
    path('payments_allocations/<int:pk>/detail/', views.PaymentAllocationDetailView.as_view(), name='payment_allocation_detail'),
    path('payments_allocations/<int:pk>/update/', views.PaymentAllocationUpdateView.as_view(), name='payment_allocation_update'),
    path('payments_allocations/<int:pk>/delete/', views.PaymentAllocationDeleteView.as_view(), name='payment_allocation_delete'),
    path('payment/<int:payment_id>/payments_allocations/', views.PaymentAllocationListView.as_view(), name='payments_allocations_by_payment'),
    path('installment/<int:installment_id>/payments_allocations/', views.PaymentAllocationListView.as_view(), name='payments_allocations_by_installment'),
]
