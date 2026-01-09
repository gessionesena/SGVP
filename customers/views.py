from django.db.models import ProtectedError
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView
from . import models, forms


class CustomerListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = models.Customer
    template_name = 'customer_list.html'
    context_object_name = 'customers'
    paginate_by = 10
    permission_required = 'customers.view_customer'

    def get_queryset(self):
        queryset = super().get_queryset()
        name = self.request.GET.get('name')

        if name:
            queryset = queryset.filter(name__icontains=name)
        return queryset


class CustomerCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = models.Customer
    template_name = 'customer_create.html'
    form_class = forms.CustomerForm
    success_url = reverse_lazy('customer_list')
    permission_required = 'customers.add_customer'


class CustomerDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = models.Customer
    template_name = 'customer_detail.html'
    context_object_name = 'customers'
    permission_required = 'customers.view_customer'


class CustomerUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = models.Customer
    template_name = 'customer_update.html'
    form_class = forms.CustomerForm
    success_url = reverse_lazy('customer_list')
    permission_required = 'customers.change_customer'


class CustomerDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = models.Customer
    template_name = 'customer_delete.html'
    success_url = reverse_lazy('customer_list')
    context_object_name = 'customers'
    permission_required = 'customers.delete_customer'

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        try:
            self.object.delete()
            messages.success(request, "Cliente excluído com sucesso!")
        except ProtectedError:
            messages.error(request, "Este cliente não pode ser excluído porque está vinculado a uma venda existente.")
        return redirect(self.success_url)
