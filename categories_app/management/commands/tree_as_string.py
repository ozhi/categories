from django.core.management.base import BaseCommand

from categories_app.lib.visuals import CategoryVisuals


class Command(BaseCommand):
    help = "Prints the Category tree as a string."

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        visual = CategoryVisuals()
        print(visual.tree_as_string())
