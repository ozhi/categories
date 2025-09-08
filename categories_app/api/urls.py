from django.urls import path
from django.urls.resolvers import URLPattern
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers

from categories_app.api.views import (
    CategoryViewSet,
    CategorySimilarityViewSet,
)


router = DefaultRouter()
router.register(r"categories", CategoryViewSet, basename="category")

categories_router = routers.NestedSimpleRouter(router, r"categories", lookup="category")
categories_router.register(
    r"similarities", CategorySimilarityViewSet, basename="category-similarity"
)

apidocs_urlpatterns = [
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path("docs/swagger/", SpectacularSwaggerView.as_view(url_name="schema")),
    path("docs/redoc/", SpectacularRedocView.as_view(url_name="schema")),
]

urlpatterns: list[URLPattern] = (
    router.urls + categories_router.urls + apidocs_urlpatterns
)
