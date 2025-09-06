from rest_framework import serializers
from categories_app.models import Category


class CategorySerializer(serializers.ModelSerializer):
    similar_to = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = Category
        fields = [
            "id",
            "name",
            "description",
            "parent",
            "similar_to",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "similar_to",
            "created_at",
            "updated_at",
        ]

    def validate(self, attrs):
        instance = self.instance
        new_parent = attrs.get("parent", instance.parent if instance else None)

        if instance and new_parent and new_parent != instance.parent:
            if instance.pk == new_parent.pk:
                raise serializers.ValidationError(
                    "A category cannot be its own parent."
                )

            # Check if new_parent is a descendant of instance
            if self._is_descendant(instance, new_parent):
                raise serializers.ValidationError(
                    "Cannot set a descendant category as the parent (would create a cycle)."
                )

        return attrs

    def _is_descendant(self, category, potential_descendant) -> bool:
        """
        Recursively checks if `potential_descendant` is a descendant of `category`.
        """
        if potential_descendant is None:
            return False

        # Walk up the tree from the potential descendant
        current = potential_descendant
        while current:
            if current.pk == category.pk:
                return True
            current = current.parent
        return False


class CategorySimilarityAddSerializer(serializers.Serializer):
    id = serializers.IntegerField()
