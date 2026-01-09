from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView
from . import models, forms


class PaymentAllocationListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = models.Payment_Allocation
    template_name = 'payment_allocation_list.html'
    context_object_name = 'payments_allocations'
    paginate_by = 10
    permission_required = 'payments_allocations.view_payment_allocation'

    def get_queryset(self):
        self.payment = None
        self.installment = None

        queryset = super().get_queryset().select_related(
            'payment', 'installment'
        )

        installment_id = self.kwargs.get('installment_id')
        payment_id = self.kwargs.get('payment_id')
        search_term = self.request.GET.get('q')

        if payment_id:
            self.payment = get_object_or_404(models.Payment, id=payment_id)
            return queryset.filter(payment=self.payment)

        if installment_id:
            self.installment = get_object_or_404(models.Installment, id=installment_id)
            return queryset.filter(installment=self.installment)

        if search_term:
            queryset = queryset.filter(
                Q(
                    payment__customer__name__icontains=search_term
                ) | Q(
                    installment__sale__title__icontains=search_term
                )
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['payment'] = self.payment
        context['installment'] = self.installment
        context['search_q'] = self.request.GET.get('q', '')
        return context


class PaymentAllocationCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = models.Payment_Allocation
    template_name = 'payment_allocation_create.html'
    form_class = forms.PaymentAllocationForm
    permission_required = 'payments_allocations.add_payment_allocation'

    def dispatch(self, request, *args, **kwargs):
        self.payment = None
        self.installment = None

        if 'payment_id' in kwargs:
            self.payment = get_object_or_404(
                models.Payment,
                pk=self.kwargs['payment_id']
            )
        if 'installment_id' in kwargs:
            self.installment = get_object_or_404(
                models.Installment,
                pk=self.kwargs['installment_id']
            )

        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['payment'] = self.payment
        kwargs['installment'] = self.installment
        return kwargs

    def form_valid(self, form):
        if self.payment:
            form.instance.payment = self.payment
        if self.installment:
            form.instance.installment = self.installment

        return super().form_valid(form)

    def get_success_url(self):
        if self.payment:
            return reverse(
                'payments_allocations_by_payment',
                args=[self.payment.pk]
            )
        if self.installment:
            return reverse(
                'payments_allocations_by_installment',
                args=[self.installment.pk]
            )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['payment'] = self.payment
        context['installment'] = self.installment
        return context


class PaymentAllocationDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = models.Payment_Allocation
    template_name = 'payment_allocation_detail.html'
    context_object_name = 'payments_allocations'
    permission_required = 'payments_allocations.view_payment_allocation'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        allocation = self.get_object()
        context['payment'] = allocation.payment
        context['installment'] = allocation.installment
        context['from'] = self.request.GET.get('from', 'payment')

        return context


class PaymentAllocationUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = models.Payment_Allocation
    template_name = 'payment_allocation_update.html'
    form_class = forms.PaymentAllocationForm
    permission_required = 'payments_allocations.change_payment_allocation'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        allocation = self.get_object()
        context['payment'] = allocation.payment
        context['installment'] = allocation.installment
        context['from'] = self.request.GET.get('from', 'payment')

        return context

    def get_success_url(self):
        allocation = self.get_object()
        source = self.request.GET.get('from', 'payment')

        if source:
            return reverse(
                'payments_allocations_by_installment',
                args=[allocation.installment.pk]
            )
        return reverse(
            'payments_allocations_by_payment',
            args=[allocation.payment.pk]
        )


class PaymentAllocationDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = models.Payment_Allocation
    template_name = 'payment_allocation_delete.html'
    context_object_name = 'payments_allocations'
    permission_required = 'payments_allocations.delete_payment_allocation'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        allocation = self.get_object()
        context['payment'] = allocation.payment
        context['installment'] = allocation.installment
        context['from'] = self.request.GET.get('from', 'payment')

        return context

    def get_success_url(self):
        allocation = self.get_object()
        source = self.request.GET.get('from', 'payment')

        if source:
            return reverse(
                'payments_allocations_by_installment',
                args=[allocation.installment.pk]
            )
        return reverse(
            'payments_allocations_by_payment',
            args=[allocation.payment.pk]
        )
