from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import LogoConfigSerializer
from .services.logo_service import generate_logo


class GenerateLogoView(APIView):
    def post(self, request):
        serializer = LogoConfigSerializer(data=request.data)
        if serializer.is_valid():
            try:
                # Lưu cấu hình tạm thời vào file
                import json
                import os

                from django.conf import settings

                temp_config_path = os.path.join(settings.BASE_DIR, "temp_config.json")
                with open(temp_config_path, "w") as f:
                    json.dump(serializer.validated_data, f)

                output_path = generate_logo(temp_config_path)
                return Response(
                    {"message": f"Logo created at {output_path}"},
                    status=status.HTTP_201_CREATED,
                )
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
