from django.urls import path

from . import views

app_name = "ai-ui"

urlpatterns = [
    path("chat/", views.chat_page, name="chat-page"),
    path("salvos/", views.saved_items_page, name="saved-items"),
    path("lista-compras/", views.shopping_list_page, name="shopping-list"),
]
