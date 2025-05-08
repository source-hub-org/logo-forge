
from django.core.management.base import BaseCommand
from logo_generator.services.logo_service import generate_logo


class Command(BaseCommand):
    help = "Tạo logo dạng chữ từ file JSON cấu hình"

    def add_arguments(self, parser):
        parser.add_argument(
            "config_file",
            nargs="?",
            type=str,
            default=None,
            help="Đường dẫn đến file JSON cấu hình (mặc định: default.json)",
        )

    def handle(self, *args, **options):
        config_file = options["config_file"]
        try:
            output_path = generate_logo(config_file)
            self.stdout.write(
                self.style.SUCCESS(f"Logo đã được tạo thành công: {output_path}")
            )
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Lỗi: {str(e)}"))
