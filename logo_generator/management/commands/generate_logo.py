import os

from django.core.management.base import BaseCommand
from logo_force.trim_logo import trim_image
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
        parser.add_argument(
            "--trim",
            action="store_true",
            help="Automatically trim excess transparent space from the output image",
        )

    def handle(self, *args, **options):
        config_file = options["config_file"]
        auto_trim = options["trim"]

        try:
            output_path = generate_logo(config_file)
            self.stdout.write(
                self.style.SUCCESS(f"Logo successfully created: {output_path}")
            )

            # Trim the image if requested
            if auto_trim:
                filename, ext = os.path.splitext(output_path)
                trimmed_path = f"{filename}_trimmed{ext}"

                if trim_image(output_path, trimmed_path):
                    self.stdout.write(
                        self.style.SUCCESS(f"Logo trimmed and saved as: {trimmed_path}")
                    )
                else:
                    self.stdout.write(self.style.WARNING("Could not trim the logo"))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error: {str(e)}"))
