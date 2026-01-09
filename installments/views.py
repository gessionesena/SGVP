from django.db.models import ProtectedError, Q
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse
from django.views.generic import ListView, DetailView, UpdateView, DeleteView
from . import models, forms
from payments_allocations.models import Payment_Allocation


class InstallmentListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = models.Installment
    template_name = 'installment_list.html'
    context_object_name = 'installments'
    paginate_by = 10
    permission_required = 'installments.view_installment'

    def get_queryset(self):
        queryset = super().get_queryset().select_related(
            'sale', 'sale__customer'
        )

        self.sale = None

        sale_id = self.kwargs.get('sale_id')

        if sale_id:
            self.sale = get_object_or_404(models.Sale, id=sale_id)
            queryset = queryset.filter(sale=self.sale)

        search_term = self.request.GET.get('q', '').strip()
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')

        if search_term:
            queryset = queryset.filter(
                Q(
                    sale__title__icontains=search_term
                ) | Q(
                    sale__customer__name__icontains=search_term
                )
            )
        if start_date:
            queryset = queryset.filter(due_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(due_date__lte=end_date)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sale'] = self.sale
        context['search_term'] = self.request.GET.get('q', '')
        context['filter_start_date'] = self.request.GET.get('start_date', '')
        context['filter_end_date'] = self.request.GET.get('end_date', '')
        return context


class InstallmentDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = models.Installment
    template_name = 'installment_detail.html'
    context_object_name = 'installments'
    permission_required = 'installments.view_installment'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        installment = self.get_object()
        context['sale'] = installment.sale
        return context


class InstallmentUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = models.Installment
    template_name = 'installment_update.html'
    form_class = forms.InstallmentForm
    permission_required = 'installments.change_installment'

    def form_valid(self, form):
        messages.success(self.request, "Juros e/ou comissão atualizados com sucesso!")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        installment = self.get_object()
        context['sale'] = installment.sale
        return context

    def get_success_url(self):
        installment = self.get_object()
        sale_id = installment.sale.id
        return reverse(
            'installments_by_sale', args=[sale_id]
        )


class InstallmentDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = models.Installment
    template_name = 'installment_delete.html'
    context_object_name = 'installments'
    permission_required = 'installments.delete_installment'

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        sale_id = self.object.sale.id

        has_allocations = Payment_Allocation.objects.filter(
            installment=self.object
        ).exists()

        if has_allocations:
            messages.error(
                request,
                "Exclusão falhou: Esta parcela não pode ser excluída pois possui valores alocados."
            )
            return redirect(self.get_success_url(sale_id))

        try:
            self.object.delete()
            messages.success(request, "Parcela excluída com sucesso!")

        except ProtectedError:
            messages.error(
                request,
                "Exclusão falhou: Esta parcela não pode ser excluída pois ainda possui valores alocados."
            )

        return redirect(self.get_success_url(sale_id))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        installment = self.object if hasattr(self, 'object') else self.get_object()
        context['sale'] = installment.sale
        return context

    def get_success_url(self, sale_id=None):
        if sale_id is None:
            sale_id = self.object.sale.id
        return reverse(
            'installments_by_sale', args=[sale_id]
        )
