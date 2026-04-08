from django.contrib import admin

from .models import NutritionalProfile


@admin.register(NutritionalProfile)
class NutritionalProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "age", "sex", "goal", "updated_at")

    search_fields = ("user__username", "user__email")

    list_filter = ("sex", "goal", "activity_level")
