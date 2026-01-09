from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from decimal import Decimal
from installments.models import Installment
from payments.models import Payment


class Payment_Allocation(models.Model):
    payment = models.ForeignKey(
        Payment,
        on_delete=models.PROTECT,
        related_name='payments_allocations',
        verbose_name='Pagamento'
    )
    installment = models.ForeignKey(
        Installment,
        on_delete=models.PROTECT,
        related_name='payments_allocations',
        verbose_name='Parcela'
    )
    amount_applied = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        verbose_name='Valor aplicado',
        validators=[
            MinValueValidator(Decimal('0.01'), message='O valor deve ser maior que zero.')
        ]
    )
    description = models.TextField(
        null=True,
        blank=True,
        verbose_name='Descrição'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        customer_name = self.payment.customer.name
        installment_number = self.installment.number
        installment_quantity = self.installment.sale.installment_quantity
        sale_title = self.installment.sale.title
        return (
            f"Alocação de R$ {self.amount_applied:.2f} "
            f"na Parcela {installment_number}/{installment_quantity} "
            f"da venda {sale_title}"
            f"(Cliente: {customer_name}) "
        )

    def clean(self):
        super().clean()

        if self.amount_applied is None:
            return

        remaining = self.payment.remaining_balance

        if self.pk:
            old_value = Payment_Allocation.objects.get(pk=self.pk).amount_applied
            remaining += old_value

        if self.amount_applied > remaining:
            raise ValidationError(
                f"Valor alocado R$ {self.amount_applied} excede o saldo disponível do pagamento (R$ {remaining})."
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)
