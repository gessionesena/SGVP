from django import forms
from . import models


class CustomerForm(forms.ModelForm):

    class Meta:
        model = models.Customer
        fields = ['name', 'phone', 'address', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        labels = {
            'name': 'Nome do cliente',
            'phone': 'Telefone',
            'address': 'Endereço',
            'description': 'Descrição',
        }
