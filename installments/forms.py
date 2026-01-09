from django import forms
from . import models


class InstallmentForm(forms.ModelForm):

    class Meta:
        model = models.Installment
        fields = ['commission_value', 'late_fee_value', 'description']
        widgets = {
            'commission_value': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01'
            }),
            'late_fee_value': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
        }
        labels = {
            'commission_value': 'Valor da comissão',
            'late_fee_value': 'Juros por atraso',
            'description': 'Descrição',
        }
