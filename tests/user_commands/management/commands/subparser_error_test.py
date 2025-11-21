from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def add_arguments(self, parser):
        subparsers = parser.add_subparsers(required=True)
        create = subparsers.add_parser("create")
        create.add_argument("name")

    def handle(self, *args, **options):
        pass
