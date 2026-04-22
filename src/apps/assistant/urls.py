from django.urls import path
from . import views

app_name = "assistant"

urlpatterns = [
    path("chat/", views.chat_page, name="chat-page"),
    path("api/chat/", views.DietAssistantChatAPIView.as_view(), name="api-chat"),
]
