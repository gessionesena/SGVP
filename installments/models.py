from django.db import models
from django.db.models import Sum
from decimal import Decimal, ROUND_HALF_UP
from sales.models import Sale


class Installment(models.Model):
    sale = models.ForeignKey(
        Sale,
        on_delete=models.PROTECT,
        related_name='installments',
        verbose_name='Título da venda'
    )
    number = models.PositiveSmallIntegerField(verbose_name='Número da parcela')
    due_date = models.DateField(verbose_name='Data do vencimento')
    amount = models.DecimalField(max_digits=20, decimal_places=2, verbose_name='Valor principal')
    commission_value = models.DecimalField(
        default=0,
        max_digits=20,
        decimal_places=2,
        verbose_name='Comissão'
    )
    late_fee_value = models.DecimalField(
        default=0,
        max_digits=20,
        decimal_places=2,
        verbose_name='Juros por atraso'
    )
    amount_total = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        verbose_name='Valor total'
    )
    description = models.TextField(null=True, blank=True, verbose_name='Descrição')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['due_date']

    def save(self, *args, **kwargs):
        self.amount_total = sum([
            self.amount or Decimal('0.00'),
            self.commission_value or Decimal('0.00'),
            self.late_fee_value or Decimal('0.00')
        ])
        super().save(*args, **kwargs)

    def __str__(self):
        installment_quantity = self.sale.installment_quantity
        due_date_formatted = self.due_date.strftime('%d/%m/%Y')
        return (
            f"#{self.id} - Parcela: {self.number}/{installment_quantity} | R$ {self.amount_total:.2f} | Vencimento: {due_date_formatted} | Venda {self.sale.id}: {self.sale.title} | {self.sale.customer.name}"
        )

    @property
    def total_paid_installment(self):
        from payments_allocations.models import Payment_Allocation
        total = Payment_Allocation.objects.filter(
            installment=self
        ).aggregate(
            total=Sum('amount_applied')
        )['total'] or Decimal('0.00')
        return total.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    @property
    def remaining_balance_installment(self):
        balance = self.amount_total - self.total_paid_installment
        return balance.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    @property
    def is_paid_off_installment(self):
        return self.remaining_balance_installment <= Decimal('0.01')
