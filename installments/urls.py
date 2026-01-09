from django.urls import path
from . import views


urlpatterns = [
    path('installments/list/', views.InstallmentListView.as_view(), name='installment_list'),
    path('installments/<int:pk>/detail/', views.InstallmentDetailView.as_view(), name='installment_detail'),
    path('installments/<int:pk>/update/', views.InstallmentUpdateView.as_view(), name='installment_update'),
    path('installments/<int:pk>/delete/', views.InstallmentDeleteView.as_view(), name='installment_delete'),
    path('sale/<int:sale_id>/installments/', views.InstallmentListView.as_view(), name='installments_by_sale'),
]
