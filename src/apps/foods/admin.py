from django.contrib import admin

from .models import Food


@admin.register(Food)
class FoodAdmin(admin.ModelAdmin):
    list_display = ("name", "kcal_per_100g", "source")

    search_fields = ("name", "source", "outsource_fdc_id")

    list_filter = ("source",)
