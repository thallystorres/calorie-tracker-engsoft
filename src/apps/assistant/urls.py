from django.urls import path

from . import views

app_name = "assistant"

urlpatterns = [
    path("chat/", views.chat_page, name="chat-page"),
    path("api/chat/", views.DietAssistantChatAPIView.as_view(), name="api-chat"),
    path(
        "api/save-content/",
        views.SaveAIContentAPIView.as_view(),
        name="api-save-content",
    ),
    path("salvos/", views.saved_items_page, name="saved-items"),
    path("api/delete-item/", views.delete_saved_item, name="api-delete-item"),
    path("api/edit-item-ai/", views.edit_saved_item_with_ai, name="api-edit-item-ai"),
    path("lista-compras/", views.shopping_list_page, name="shopping-list"),
]
