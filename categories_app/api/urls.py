from django.urls import path
from django.urls.resolvers import URLPattern

from categories_app.api.views.category_list import CategoryListView
from categories_app.api.views.category_retrieve import CategoryRetrieveView


urlpatterns: list[URLPattern] = [
    path("categories/", CategoryListView.as_view(), name="api_category_list"),
    path(
        "categories/<int:pk>/",
        CategoryRetrieveView.as_view(),
        name="api_category_retrieve",
    ),
]
