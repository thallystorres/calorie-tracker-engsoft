from django.contrib import admin
from django.urls import include, path

from . import handlers

handler500 = handlers.server_error
handler404 = handlers.not_found

urlpatterns = [
  path("admin/", admin.site.urls),
  path("", include("apps.study_tracker.ui_urls")),
  path("accounts/", include("apps.accounts.ui_urls", namespace="accounts-ui")),  # Mantido do framework core
  path("profile/", include("apps.study_profiles.ui_urls")),
  path("contents/", include("apps.contents.ui_urls", namespace="contents-ui")),
  path("ai/", include("apps.study_ai_engine.ui_urls")),
  path("api/accounts/", include("apps.accounts.urls")),
  path("api/contents/", include("apps.contents.urls")),
  path("api/profiles/", include("apps.study_profiles.urls")),
  path("api/tracker/", include("apps.study_tracker.urls")),
  path("api/ai/", include("apps.study_ai_engine.urls")),
]
