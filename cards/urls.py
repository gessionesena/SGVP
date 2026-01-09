from django.urls import path
from . import views


urlpatterns = [
    path('cards/list/', views.CardListView.as_view(), name='card_list'),
    path('cards/create/', views.CardCreateView.as_view(), name='card_create'),
    path('cards/<int:pk>/detail/', views.CardDetailView.as_view(), name='card_detail'),
    path('cards/<int:pk>/update/', views.CardUpdateView.as_view(), name='card_update'),
    path('cards/<int:pk>/delete/', views.CardDeleteView.as_view(), name='card_delete'),
]
