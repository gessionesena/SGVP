from django.db import models


class Customer(models.Model):
    name = models.CharField(max_length=250, verbose_name='Nome')
    phone = models.CharField(max_length=50, null=True, blank=True, verbose_name='Telefone')
    address = models.CharField(max_length=250, null=True, blank=True, verbose_name='Endereço')
    description = models.TextField(null=True, blank=True, verbose_name='Descrição')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name
