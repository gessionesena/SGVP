from django.db.models import ProtectedError
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView
from . import models, forms


class CardListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = models.Card
    template_name = 'card_list.html'
    context_object_name = 'cards'
    paginate_by = 10
    permission_required = 'cards.view_card'

    def get_queryset(self):
        queryset = super().get_queryset()
        title = self.request.GET.get('title')

        if title:
            queryset = queryset.filter(title__icontains=title)
        return queryset


class CardCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = models.Card
    template_name = 'card_create.html'
    form_class = forms.CardForm
    success_url = reverse_lazy('card_list')
    permission_required = 'cards.add_card'


class CardDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = models.Card
    template_name = 'card_detail.html'
    context_object_name = 'cards'
    permission_required = 'cards.view_card'


class CardUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = models.Card
    template_name = 'card_update.html'
    form_class = forms.CardForm
    success_url = reverse_lazy('card_list')
    permission_required = 'cards.change_card'


class CardDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = models.Card
    template_name = 'card_delete.html'
    success_url = reverse_lazy('card_list')
    context_object_name = 'cards'
    permission_required = 'cards.delete_card'

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        try:
            self.object.delete()
            messages.success(request, "Cartão excluído com sucesso!")
        except ProtectedError:
            messages.error(request, "Este cartão não pode ser excluído porque está vinculado a uma venda existente.")
        return redirect(self.success_url)
