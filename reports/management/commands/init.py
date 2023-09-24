from django.core.management.base import BaseCommand, CommandError
from reports.models import Currency


class Command(BaseCommand):
    help = "Initialize some data on database"

    data_types = [
        "currency",
    ]

    def add_arguments(self, parser):
        parser.add_argument(
            "data_type",
            type=str,
            help=f"Type of data to initialize. Select between: {self.data_types}",
        )

    def handle(self, *args, **options):
        data_type = options["data_type"]
        if data_type not in self.data_types:
            raise CommandError(f"Unknown data type: {data_type}. Select between: {self.data_types}")

        if data_type == "currency":
            currencies = [
                {"name": "won", "code": "KRW"},
            ]

            for curr in currencies:
                Currency.objects.get_or_create(name=curr["name"], code=curr["code"])

            self.stdout.write(self.style.SUCCESS("Currency initialized."))
        
        return 0