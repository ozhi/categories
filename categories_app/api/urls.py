from django.urls.resolvers import URLPattern
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

urlpatterns: list[URLPattern] = router.urls + categories_router.urls
