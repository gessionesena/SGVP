from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.db.models import ProtectedError, Q
from django.forms import ValidationError
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView
from . import models, forms, services
from payments_allocations.models import Payment_Allocation


class SaleListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = models.Sale
    template_name = 'sale_list.html'
    context_object_name = 'sales'
    paginate_by = 10
    permission_required = 'sales.view_sale'

    def get_queryset(self):
        queryset = super().get_queryset().select_related(
            'customer', 'card'
        )
        search_term = self.request.GET.get('q', '').strip()
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')

        if search_term:
            queryset = queryset.filter(
                Q(
                    title__icontains=search_term
                ) | Q(
                    customer__name__icontains=search_term
                ) | Q(
                    card__title__icontains=search_term
                )
            )
        if start_date:
            queryset = queryset.filter(sale_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(sale_date__lte=end_date)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_q'] = self.request.GET.get('q', '')
        context['filter_start_date'] = self.request.GET.get('start_date', '')
        context['filter_end_date'] = self.request.GET.get('end_date', '')
        return context


class SaleCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = models.Sale
    template_name = 'sale_create.html'
    form_class = forms.SaleForm
    success_url = reverse_lazy('sale_list')
    permission_required = 'sales.add_sale'

    def form_valid(self, form):
        response = super().form_valid(form)
        services.generate_sale_installments(self.object)
        return response


class SaleDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = models.Sale
    template_name = 'sale_detail.html'
    context_object_name = 'sales'
    permission_required = 'sales.view_sale'


class SaleUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = models.Sale
    template_name = 'sale_update.html'
    form_class = forms.SaleForm
    success_url = reverse_lazy('sale_list')
    permission_required = 'sales.change_sale'

    def form_valid(self, form):
        sale_obj = self.get_object()

        try:
            services.update_sale_with_installments(
                sale_instance_to_update=sale_obj,
                new_sale_data=form.cleaned_data
            )
            messages.success(self.request, "Venda e parcelas atualizadas com sucesso!")
            return redirect(self.get_success_url())

        except ValidationError as e:
            error_msg = e.messages if hasattr(e, 'messages') else str(e)
            if isinstance(error_msg, (list, tuple)):
                error_msg = " ".join(map(str, error_msg))

            form.add_error(None, error_msg)
            messages.error(self.request, error_msg)
            return self.form_invalid(form)


class SaleDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = models.Sale
    template_name = 'sale_delete.html'
    success_url = reverse_lazy('sale_list')
    context_object_name = 'sales'
    permission_required = 'sales.delete_sale'

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        if Payment_Allocation.objects.filter(installment__sale=self.object).exists():
            messages.error(
                request,
                "Exclusão falhou: Esta venda não pode ser excluída pois já possui pagamentos financeiros registrados."
            )
            return redirect(self.success_url)

        try:
            self.object.delete()
            messages.success(request, "Venda excluída com sucesso!")

        except ProtectedError:
            messages.error(
                request,
                "Exclusão falhou: Esta venda não pode ser excluída pois ainda possui parcelas associadas. Delete as parcelas primeiro (se não houver pagamentos)."
            )
        return redirect(self.success_url)
