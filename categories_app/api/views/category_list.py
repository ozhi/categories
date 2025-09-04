from rest_framework import generics
from categories_app.models import Category
from categories_app.api.serializers import CategorySerializer


class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
