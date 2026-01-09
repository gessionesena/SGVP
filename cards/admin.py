from django.contrib import admin
from . import models


@admin.register(models.Card)
class CardAdmin(admin.ModelAdmin):
    list_display = ('title', 'description',)
    search_fields = ('title',)
