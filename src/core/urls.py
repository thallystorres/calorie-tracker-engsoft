from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("apps.accounts.ui_urls")),
    path("foods/", include("apps.foods.ui_urls")),
    path("tracker/", include("apps.tracker.ui_urls")),
    path("profiles/", include("apps.profiles.ui_urls")),
    path("api/accounts/", include("apps.accounts.urls")),
    path("api/profiles/", include("apps.profiles.urls")),
    path("api/foods/", include("apps.foods.urls")),
    path("api/tracker/", include("apps.tracker.urls")),
    path("assistant/", include("apps.assistant.urls")),
]
