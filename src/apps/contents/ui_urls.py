from django.urls import path
from . import ui_views

app_name = "contents-ui"

urlpatterns = [
    path("new/", ui_views.content_create_page, name="content-create"),
]
