from django.urls import path
from . import views

app_name = "contents"

urlpatterns = [
    path("", views.ContentListCreateView.as_view(), name="list-create"),
    path("search/", views.ContentSearchView.as_view(), name="search"),
    path("<int:content_id>/", views.ContentDetailView.as_view(), name="detail"),
]
