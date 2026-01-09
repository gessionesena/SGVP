from django.db.models import ProtectedError
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView
from . import models, forms
from payments_allocations.models import Payment_Allocation


class PaymentListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = models.Payment
    template_name = 'payment_list.html'
    context_object_name = 'payments'
    paginate_by = 10
    permission_required = 'payments.view_payment'

    def get_queryset(self):
        queryset = super().get_queryset().select_related(
            'customer'
        )
        customer = self.request.GET.get('customer')
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')

        if customer:
            queryset = queryset.filter(customer__name__icontains=customer)
        if start_date:
            queryset = queryset.filter(payment_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(payment_date__lte=end_date)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter_start_date'] = self.request.GET.get('start_date', '')
        context['filter_end_date'] = self.request.GET.get('end_date', '')
        return context


class PaymentCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = models.Payment
    template_name = 'payment_create.html'
    form_class = forms.PaymentForm
    success_url = reverse_lazy('payment_list')
    permission_required = 'payments.add_payment'


class PaymentDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = models.Payment
    template_name = 'payment_detail.html'
    context_object_name = 'payments'
    permission_required = 'payments.view_payment'


class PaymentUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = models.Payment
    template_name = 'payment_update.html'
    form_class = forms.PaymentForm
    success_url = reverse_lazy('payment_list')
    permission_required = 'payments.change_payment'

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()

        if obj.payments_allocations.exists():
            messages.error(request, "Este pagamento possui alocações e não pode ser editado.")
            return redirect('payment_list')

        return super().dispatch(request, *args, **kwargs)


class PaymentDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = models.Payment
    template_name = 'payment_delete.html'
    success_url = reverse_lazy('payment_list')
    context_object_name = 'payments'
    permission_required = 'payments.delete_payment'

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        if Payment_Allocation.objects.filter(payment=self.object).exists():
            messages.error(
                request,
                "Exclusão falhou: Este pagamento não pode ser excluído pois possui valores alocados em parcelas."
            )
            return redirect(self.success_url)

        try:
            self.object.delete()
            messages.success(request, "Pagamento excluído com sucesso!")

        except ProtectedError:
            messages.error(
                request,
                "Exclusão falhou: Este pagamento não pode ser excluído pois ainda possui valores alocados em parcelas. Delete as alocações primeiro."
            )
        return redirect(self.success_url)
