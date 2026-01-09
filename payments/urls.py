from django.urls import path
from . import views


urlpatterns = [
    path('payments/list/', views.PaymentListView.as_view(), name='payment_list'),
    path('payments/create/', views.PaymentCreateView.as_view(), name='payment_create'),
    path('payments/<int:pk>/detail/', views.PaymentDetailView.as_view(), name='payment_detail'),
    path('payments<int:pk>/update/', views.PaymentUpdateView.as_view(), name='payment_update'),
    path('payments/<int:pk>/delete/', views.PaymentDeleteView.as_view(), name='payment_delete'),
]
