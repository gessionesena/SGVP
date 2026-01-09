from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


class Card(models.Model):
    title = models.CharField(max_length=200, verbose_name='Título do Cartão')
    payment_due_day = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(31)
        ],
    )
    description = models.TextField(null=True, blank=True, verbose_name='Descrição')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['title']

    def __str__(self):
        return self.title
