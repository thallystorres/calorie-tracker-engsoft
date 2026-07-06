from django.contrib import admin
from django.urls import include, path

from . import handlers

handler500 = handlers.server_error
handler404 = handlers.not_found

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("apps.accounts.ui_urls")),
    path("api/accounts/", include("apps.accounts.urls")),
    path("academia/", include("apps.academia.ui_urls")),
    path("api/academia/", include("apps.academia.urls")),
]
