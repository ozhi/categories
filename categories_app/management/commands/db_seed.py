from django.core.management.base import BaseCommand

from categories_app.lib.db_seed import create_example_categories


class Command(BaseCommand):
    help = "Seeds the db with sample data for testing or development."

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        create_example_categories()
        self.stdout.write(self.style.SUCCESS("DB seeded successfully"))
