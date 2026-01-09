from django.urls import path
from . import views


urlpatterns = [
    path('sales/list/', views.SaleListView.as_view(), name='sale_list'),
    path('sales/create/', views.SaleCreateView.as_view(), name='sale_create'),
    path('sales/<int:pk>/detail/', views.SaleDetailView.as_view(), name='sale_detail'),
    path('sales/<int:pk>/update/', views.SaleUpdateView.as_view(), name='sale_update'),
    path('sales/<int:pk>/delete/', views.SaleDeleteView.as_view(), name='sale_delete'),
]
