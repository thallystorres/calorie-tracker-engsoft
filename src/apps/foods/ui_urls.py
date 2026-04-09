from django.urls import path

from . import ui_views

app_name = "foods-ui"

urlpatterns = [
    path("new/", ui_views.food_create_page, name="food-create"),
]
