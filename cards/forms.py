from django import forms
from . import models


class CardForm(forms.ModelForm):

    class Meta:
        model = models.Card
        fields = ['title', 'payment_due_day', 'description']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'payment_due_day': forms.NumberInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        labels = {
            'title': 'Título do Cartão',
            'payment_due_day': 'Dia de vencimento do pagamento',
            'description': 'Descrição',
        }
