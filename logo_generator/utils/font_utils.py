import json
import os

import requests
from django.conf import settings


def get_api_variant(weight, style):
    """Chuyển đổi weight và style thành variant của Google Fonts."""
    if weight == 400 and style == "normal":
        return "regular"
    elif weight == 400 and style == "italic":
        return "italic"
    else:
        base = str(weight)
        if style == "italic":
            base += "italic"
        return base


def get_font_path(font_family, weight, style):
    """Tải font từ Google Fonts hoặc lấy từ cache."""
    variant = get_api_variant(weight, style)
    cache_dir = os.path.join(settings.BASE_DIR, "font_cache")
    os.makedirs(cache_dir, exist_ok=True)
    font_file = f"{font_family.replace(' ', '_')}_{variant}.ttf"
    local_path = os.path.join(cache_dir, font_file)

    if os.path.exists(local_path):
        return local_path

    # Cache danh sách font
    font_list_cache = os.path.join(cache_dir, "font_list.json")
    fonts = None
    if os.path.exists(font_list_cache):
        with open(font_list_cache) as f:
            fonts = json.load(f)

    if not fonts:
        if not settings.GOOGLE_FONTS_API_KEY:
            raise Exception("Thiếu GOOGLE_FONTS_API_KEY trong cấu hình môi trường")

        # Tải danh sách font từ Google Fonts API
        try:
            response = requests.get(
                f"https://www.googleapis.com/webfonts/v1/webfonts?key={settings.GOOGLE_FONTS_API_KEY}",
                timeout=10,
            )
            response.raise_for_status()
            fonts = response.json().get("items", [])
            # Lưu danh sách font vào cache
            with open(font_list_cache, "w") as f:
                json.dump(fonts, f)
        except requests.exceptions.RequestException as e:
            raise Exception(
                f"Không thể lấy danh sách font từ Google Fonts API: {str(e)}"
            )

    # Tìm font
    for font in fonts:
        if font["family"].lower() == font_family.lower():
            files = font.get("files", {})
            if variant in files:
                font_url = files[variant]
                try:
                    font_response = requests.get(font_url, timeout=10)
                    font_response.raise_for_status()
                    with open(local_path, "wb") as f:
                        f.write(font_response.content)
                    return local_path
                except requests.exceptions.RequestException as e:
                    raise Exception(f"Không thể tải font từ {font_url}: {str(e)}")
            else:
                raise Exception(
                    f"Không tìm thấy variant {variant} cho font {font_family}"
                )
    raise Exception(f"Không tìm thấy font family {font_family}")
