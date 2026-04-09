from django.urls import path

from .views import FoodRestrictionDetailView, FoodRestrictionListCreateView, ProfileView

app_name = "profiles"

urlpatterns = [
    # Rotas base para o perfil (POST, PATCH) -> /api/profiles/
    path("", ProfileView.as_view(), name="profile"),
    # Rotas para restrições alimentares
    # POST -> /api/profiles/me/restrictions/
    path(
        "me/restrictions/",
        FoodRestrictionListCreateView.as_view(),
        name="restrictions-list-create",
    ),
    # DELETE -> /api/profiles/me/restrictions/<id>/
    path(
        "me/restrictions/<int:pk>/",
        FoodRestrictionDetailView.as_view(),
        name="restrictions-detail",
    ),
]
