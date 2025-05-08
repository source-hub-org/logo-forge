import json
import os

import requests
from django.conf import settings


def get_api_variant(weight, style):
    """Convert weight and style to Google Fonts variant format."""
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
    """Download font from Google Fonts or retrieve from cache."""
    variant = get_api_variant(weight, style)
    cache_dir = os.path.join(settings.BASE_DIR, "font_cache")
    os.makedirs(cache_dir, exist_ok=True)
    font_file = f"{font_family.replace(' ', '_')}_{variant}.ttf"
    local_path = os.path.join(cache_dir, font_file)

    if os.path.exists(local_path):
        return local_path

    # Cache font list
    font_list_cache = os.path.join(cache_dir, "font_list.json")
    fonts = None
    if os.path.exists(font_list_cache):
        with open(font_list_cache) as f:
            fonts = json.load(f)

    if not fonts:
        if not settings.GOOGLE_FONTS_API_KEY:
            raise Exception("Missing GOOGLE_FONTS_API_KEY in environment configuration")

        # Download font list from Google Fonts API
        try:
            response = requests.get(
                f"https://www.googleapis.com/webfonts/v1/webfonts?key={settings.GOOGLE_FONTS_API_KEY}",
                timeout=10,
            )
            response.raise_for_status()
            fonts = response.json().get("items", [])
            # Save font list to cache
            with open(font_list_cache, "w") as f:
                json.dump(fonts, f)
        except requests.exceptions.RequestException as e:
            raise Exception(
                f"Unable to retrieve font list from Google Fonts API: {str(e)}"
            )

    # Find font
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
                    raise Exception(
                        f"Unable to download font from {font_url}: {str(e)}"
                    )
            else:
                raise Exception(f"Variant {variant} not found for font {font_family}")
    raise Exception(f"Font family {font_family} not found")
