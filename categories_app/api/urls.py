from django.urls.resolvers import URLPattern
from rest_framework.routers import DefaultRouter

from categories_app.api.views.category_viewset import CategoryViewSet


router = DefaultRouter()
router.register(r"categories", CategoryViewSet, basename="category")
urlpatterns: list[URLPattern] = router.urls
