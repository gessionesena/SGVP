from django.db import models
from django.db.models import Sum
from django.core.validators import MaxValueValidator, MinValueValidator
from decimal import Decimal, ROUND_HALF_UP
from cards.models import Card
from categories.models import Category
from customers.models import Customer


class Sale(models.Model):
    title = models.CharField(
        max_length=250,
        verbose_name='Título'
    )
    customer = models.ForeignKey(
        Customer,
        on_delete=models.PROTECT,
        related_name='sales',
        verbose_name='Cliente'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='sales',
        verbose_name='Categoria'
    )
    card = models.ForeignKey(
        Card,
        on_delete=models.PROTECT,
        related_name='sales',
        verbose_name='Cartão'
    )
    sale_date = models.DateField(
        verbose_name='Data da venda'
    )
    cost_price = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        verbose_name='Preço de custo'
    )
    selling_price = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        verbose_name='Preço de venda'
    )
    installment_quantity = models.PositiveSmallIntegerField(
        verbose_name='Quantidade de parcelas',
        validators=[
            MinValueValidator(1, message='O número de parcelas deve ser igual ou maior que 1.'),
            MaxValueValidator(12, message='O número máximo de parcelas é 12.')
        ]
    )
    description = models.TextField(null=True, blank=True, verbose_name='Descrição')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-sale_date']

    def __str__(self):
        customer_name = self.customer.name
        return f"#{self.id} - {self.title} | {self.card} | {customer_name}"

    @property
    def total_installments_amount(self):
        from installments.models import Installment
        return Installment.objects.filter(sale=self).aggregate(
            total=Sum('amount_total')
        )['total'] or Decimal('0.00')

    @property
    def total_paid(self):
        from payments_allocations.models import Payment_Allocation
        total = Payment_Allocation.objects.filter(
            installment__sale=self
        ).aggregate(
            total=Sum('amount_applied')
        )['total'] or Decimal('0.00')
        return total.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    @property
    def remaining_balance(self):
        return self.total_installments_amount - self.total_paid

    @property
    def is_paid_off(self):
        return self.remaining_balance <= Decimal('0.009')
