from django.core.management.base import BaseCommand

from categories_app.lib.visuals import CategoryVisuals


class Command(BaseCommand):
    help = "Saves the Category tree with color-coded similarity as local file tree.png"
    # TODO: As the image represents the db data and is not request-specific,
    # it can be periodically cached and returned by an API endpoint.

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        visual = CategoryVisuals()
        visual.save_tree_as_image("tree.png")
