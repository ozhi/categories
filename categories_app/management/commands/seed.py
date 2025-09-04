from django.core.management.base import BaseCommand

from categories_app.models import Category


class Command(BaseCommand):
    help = "Seeds the db with sample data for testing or development."

    def add_arguments(self, parser):
        pass  # parser.add_argument("category_count", nargs="+", type=int)

    def handle(self, *args, **options):
        tech, _ = Category.objects.update_or_create(
            name="Tech", description="All things tech"
        )
        computers, _ = Category.objects.update_or_create(name="Computers", parent=tech)
        _laptops, _ = Category.objects.update_or_create(
            name="Laptops", parent=computers
        )
        _desktops, _ = Category.objects.update_or_create(
            name="Desktops", parent=computers
        )
        audio, _ = Category.objects.update_or_create(name="Audio", parent=tech)
        headphones, _ = Category.objects.update_or_create(
            name="Headphones", parent=audio
        )
        wireless_headphones, _ = Category.objects.update_or_create(
            name="Wireless headphones", parent=headphones
        )
        _, _ = Category.objects.update_or_create(
            name="In-ear wireless headphones", parent=wireless_headphones
        )
        _, _ = Category.objects.update_or_create(
            name="Over-ear wireless headphones", parent=wireless_headphones
        )

        food, _ = Category.objects.update_or_create(name="Food")
        fresh_produce, _ = Category.objects.update_or_create(
            name="Fresh produce", parent=food
        )
        vegetables, _ = Category.objects.update_or_create(
            name="Vegetables", parent=fresh_produce
        )
        potatoes, _ = Category.objects.update_or_create(
            name="Potatoes", parent=vegetables
        )
        _sweet_potatoes, _ = Category.objects.update_or_create(
            name="Sweet potatoes", parent=potatoes
        )

        _books, _ = Category.objects.update_or_create(name="Books")

        self.stdout.write(self.style.SUCCESS("DB seeded successfully"))
