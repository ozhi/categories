from django.core.management.base import BaseCommand

from categories_app.models import Category


class Command(BaseCommand):
    help = "Seeds the db with sample data for testing or development."

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        tech, _ = Category.objects.update_or_create(
            name="Tech",
            defaults={
                "description": "All things tech",
                "parent": None,
            },
        )
        computers, _ = Category.objects.update_or_create(
            name="Computers",
            defaults={
                "parent": tech,
            },
        )
        laptops, _ = Category.objects.update_or_create(
            name="Laptops",
            defaults={
                "parent": computers,
            },
        )
        desktops, _ = Category.objects.update_or_create(
            name="Desktops",
            defaults={
                "parent": computers,
            },
        )
        audio, _ = Category.objects.update_or_create(
            name="Audio",
            defaults={
                "parent": tech,
            },
        )
        headphones, _ = Category.objects.update_or_create(
            name="Headphones",
            defaults={
                "parent": audio,
            },
        )
        wireless_headphones, _ = Category.objects.update_or_create(
            name="Wireless headphones",
            defaults={
                "parent": headphones,
            },
        )
        _, _ = Category.objects.update_or_create(
            name="In-ear wireless headphones",
            defaults={
                "parent": wireless_headphones,
            },
        )
        _, _ = Category.objects.update_or_create(
            name="Over-ear wireless headphones",
            defaults={
                "parent": wireless_headphones,
            },
        )

        food, _ = Category.objects.update_or_create(
            name="Food",
            defaults={
                "parent": None,
            },
        )
        fresh_produce, _ = Category.objects.update_or_create(
            name="Fresh produce",
            defaults={
                "parent": food,
            },
        )
        vegetables, _ = Category.objects.update_or_create(
            name="Vegetables",
            defaults={
                "parent": fresh_produce,
            },
        )
        potatoes, _ = Category.objects.update_or_create(
            name="Potatoes",
            defaults={
                "parent": vegetables,
            },
        )
        sweet_potatoes, _ = Category.objects.update_or_create(
            name="Sweet potatoes",
            defaults={
                "parent": potatoes,
            },
        )

        books, _ = Category.objects.update_or_create(
            name="Books",
            defaults={
                "parent": None,
            },
        )

        # Similarities.
        computers.similar_to.add(laptops, desktops)
        laptops.similar_to.add(desktops)
        books.similar_to.add(computers)
        potatoes.similar_to.add(sweet_potatoes)

        self.stdout.write(self.style.SUCCESS("DB seeded successfully"))
