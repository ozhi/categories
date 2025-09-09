from django.core.management.base import BaseCommand

from categories_app.lib.similarity_graph import SimilarityGraph


class Command(BaseCommand):
    help = "Prints the ids of the Categories in the longest rabbit hole."

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        path = SimilarityGraph().compute_longest_rabbit_hole()
        print(path)
