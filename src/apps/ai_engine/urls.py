from django.urls import path

from . import views

app_name = "ai"

urlpatterns = [
    path("suggest_meal/", views.SuggestMealView.as_view(), name="suggest_meal"),
    path("api/chat/", views.DietAssistantChatAPIView.as_view(), name="api-chat"),
    path(
        "api/save-content/",
        views.SaveAIContentAPIView.as_view(),
        name="api-save-content",
    ),
    path("api/delete-item/", views.delete_saved_item, name="api-delete-item"),
    path("api/edit-item-ai/", views.edit_saved_item_with_ai, name="api-edit-item-ai"),
]
