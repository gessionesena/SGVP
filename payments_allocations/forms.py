from django import forms
from . import models


class PaymentAllocationForm(forms.ModelForm):
    class Meta:
        model = models.Payment_Allocation
        fields = ['payment', 'installment', 'amount_applied', 'description']
        widgets = {
            'payment': forms.Select(attrs={'class': 'form-control'}),
            'installment': forms.Select(attrs={'class': 'form-control'}),
            'amount_applied': forms.NumberInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        labels = {
            'payment': 'Pagamento',
            'installment': 'Parcela',
            'amount_applied': 'Valor alocado na Parcela',
            'description': 'Descrição',
        }

    def __init__(self, *args, payment=None, installment=None, **kwargs):
        super().__init__(*args, **kwargs)

        if payment:
            self.fields['payment'].initial = payment
            self.fields['payment'].disabled = True

        if installment:
            self.fields['installment'].initial = installment
            self.fields['installment'].disabled = True

    def clean_amount_applied(self):
        from payments.models import Payment

        payment = self.cleaned_data.get('payment') or self.instance.payment
        amount = self.cleaned_data['amount_applied']

        if amount is None:
            return

        if payment and not isinstance(payment, Payment):
            payment = Payment.objects.get(pk=int(payment))

        if payment is None:
            raise forms.ValidationError("Pagamento não informado.")

        remaining = payment.remaining_balance

        if self.instance.pk:
            old = self.instance.amount_applied
            remaining += old

        if amount > remaining:
            raise forms.ValidationError(
                f"Valor informado é maior que o saldo disponível (R$ {remaining})."
            )

        return amount
