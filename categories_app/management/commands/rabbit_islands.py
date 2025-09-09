from django.core.management.base import BaseCommand

from categories_app.lib.similarity_graph import SimilarityGraph


class Command(BaseCommand):
    help = "Prints the ids of the Categories in all the rabbit islands."

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        islands = SimilarityGraph().compute_rabbit_islands()
        print(islands)
