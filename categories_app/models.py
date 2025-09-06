from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=300, null=True, blank=True)

    # Use FileSystemStorage for local development.
    # Consider using AWS S3 or another cloud storage for production.
    image = models.ImageField(upload_to="uploads/category_images", max_length=350)

    # Parent is the direct ancestor category.
    # on_delete=models.RESTRICT prevents deleting a category if it has children.
    parent = models.ForeignKey(
        to="Category",
        on_delete=models.RESTRICT,
        null=True,
        blank=True,
        related_name="children",
    )

    # A category can be similar to multiple other categories.
    # Symmetry - automatically reflected in the db by Django, A~B implies B~A.
    # Transitiveness - not enforced, if A~B and B~C, A~C may or may not be true.
    # Reflexiveness - forbidden, we can not have A~A.
    similar_to = models.ManyToManyField(to="self", symmetrical=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"Category {self.id} ({self.name})"

    class Meta:
        verbose_name_plural = "categories"
