from django.db import models
from django.db.models import Sum
from decimal import Decimal, ROUND_HALF_UP
from customers.models import Customer


PAYMENT_METHOD_CHOICES = (
    ('PIX', 'Pix'),
    ('DINHEIRO', 'Dinheiro'),
)


class Payment(models.Model):
    customer = models.ForeignKey(
        Customer,
        on_delete=models.PROTECT,
        related_name='payments',
        verbose_name='Cliente'
    )
    value = models.DecimalField(max_digits=20, decimal_places=2, verbose_name='Valor do pagamento')
    payment_date = models.DateField(verbose_name='Data do pagamento')
    method = models.CharField(
        max_length=10,
        choices=PAYMENT_METHOD_CHOICES,
        verbose_name='Método do pagamento'
    )
    description = models.TextField(null=True, blank=True, verbose_name='Descrição')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-payment_date']

    def __str__(self):
        payment_date_formatted = self.payment_date.strftime('%d/%m/%Y')
        return (
            f"{self.id}# Valor: R$ {self.value} | {payment_date_formatted} | {self.customer.name}"
        )

    @property
    def total_payments_allocations(self):
        from payments_allocations.models import Payment_Allocation
        return Payment_Allocation.objects.filter(payment=self).aggregate(
            total=Sum('amount_applied')
        )['total'] or Decimal('0.00')

    @property
    def remaining_balance(self):
        if self.value is None:
            return Decimal('0.00')
        balance = self.value - self.total_payments_allocations
        return balance.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    @property
    def is_fully_allocated(self):
        return self.remaining_balance <= Decimal('0.01')
