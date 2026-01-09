from django import forms
from . import models


class SaleForm(forms.ModelForm):

    class Meta:
        model = models.Sale
        fields = ['title', 'customer', 'category', 'card', 'sale_date', 'cost_price', 'selling_price', 'installment_quantity', 'description']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'customer': forms.Select(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'card': forms.Select(attrs={'class': 'form-control'}),
            'sale_date': forms.DateInput(
                attrs={
                    'class': 'form-control',
                    'type': 'date'
                },
                format='%Y-%m-%d'
            ),
            'cost_price': forms.NumberInput(attrs={'class': 'form-control'}),
            'selling_price': forms.NumberInput(attrs={'class': 'form-control'}),
            'installment_quantity': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'min': '1',
                    'max': '12'
                }
            ),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        labels = {
            'title': 'Título da venda',
            'customer': 'Cliente',
            'category': 'Categoria',
            'card': 'Cartão',
            'sale_date': 'Data da Venda',
            'cost_price': 'Preço de custo',
            'selling_price': 'Preço de venda',
            'installment_quantity': 'Quantidade de parcelas',
            'description': 'Descrição',
        }
