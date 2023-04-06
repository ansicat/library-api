from django.core.management import call_command
from django.core.management.commands.migrate import Command as MigrateCommand


class Command(MigrateCommand):
    def add_arguments(self, parser):
        super().add_arguments(parser)

        parser.add_argument(
            "--with_test_data",
            action="store_true",
            help="Load test data for Library service database.",
        )

    def handle(self, *args, **options):
        super().handle(*args, **options)

        if options["with_test_data"]:
            call_command("loaddata", "library_db_data.json")
