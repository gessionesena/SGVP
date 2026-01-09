from django.contrib import admin
from . import models


@admin.register(models.Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'address', 'description',)
    search_fields = ('name',)
