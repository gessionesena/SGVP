from django import forms
from . import models


class PaymentForm(forms.ModelForm):

    class Meta:
        model = models.Payment
        fields = ['customer', 'value', 'payment_date', 'method', 'description']
        widgets = {
            'customer': forms.Select(attrs={'class': 'form-control'}),
            'value': forms.NumberInput(attrs={'class': 'form-control'}),
            'payment_date': forms.DateInput(
                attrs={
                    'class': 'form-control',
                    'type': 'date'
                },
                format='%Y-%m-%d'
            ),
            'method': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        labels = {
            'customer': 'Cliente',
            'value': 'Valor',
            'payment_date': 'Data do Pagamento',
            'method': 'Método do Pagamento',
            'description': 'Descrição',
        }

    def clean(self):
        cleaned = super().clean()
        obj = self.instance

        if obj.pk and obj.payments_allocations.exists():
            raise forms.ValidationError(
                "Este pagamento possui alocações e não pode ser editado."
            )

        return cleaned

    def clean_value(self):
        value = self.cleaned_data.get('value')
        if value is None:
            raise forms.ValidationError('Informe o valor do Pagamento')
        return value
