from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=300, null=True, blank=True)
    image = models.ImageField(upload_to="uploads/category_images", max_length=350)

    # Parent is the direct ancestor category.
    # on_delete=models.RESTRICT prevents deleting a category if it has children.
    parent = models.ForeignKey(
        "Category",
        on_delete=models.RESTRICT,
        null=True,
        blank=True,
        related_name="children",
    )

    class Meta:
        verbose_name_plural = "categories"
