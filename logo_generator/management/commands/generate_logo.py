from django.core.management.base import BaseCommand
from logo_generator.services.logo_service import generate_logo


class Command(BaseCommand):
    help = "Generate a text logo from a JSON configuration file"

    def add_arguments(self, parser):
        parser.add_argument(
            "config_file",
            nargs="?",
            type=str,
            default=None,
            help="Path to the JSON configuration file (default: default.json)",
        )

    def handle(self, *args, **options):
        config_file = options["config_file"]
        try:
            output_path = generate_logo(config_file)
            self.stdout.write(
                self.style.SUCCESS(f"Logo successfully created: {output_path}")
            )
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error: {str(e)}"))
