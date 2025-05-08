import json

from django.conf import settings
from logo_generator.utils.font_utils import get_font_path
from logo_generator.utils.image_utils import create_logo_image, draw_text_with_spacing
from PIL import ImageFont


def generate_logo(config_path=None):
    """Generate a logo from a JSON configuration file."""
    if not config_path:
        config_path = settings.DEFAULT_CONFIG_PATH

    try:
        with open(config_path) as f:
            config = json.load(f)
    except FileNotFoundError:
        raise Exception(f"File not found: {config_path}")

    image, draw = create_logo_image(config)

    site_name_config = config["site_name"]
    site_name_font_path = get_font_path(
        site_name_config["font_family"],
        site_name_config["font_weight"],
        site_name_config["font_style"],
    )
    site_name_font = ImageFont.truetype(
        site_name_font_path, site_name_config["font_size"]
    )
    site_name_color = tuple(
        int(site_name_config["color"][i : i + 2], 16) for i in (1, 3, 5)
    ) + (255,)
    site_name_position = (
        site_name_config["position"]["x"],
        site_name_config["position"]["y"],
    )
    site_name_text = site_name_config["text"]
    site_name_letter_spacing = site_name_config.get("letter_spacing", 0)
    site_name_word_spacing = site_name_config.get("word_spacing", 0)

    draw_text_with_spacing(
        draw,
        site_name_position,
        site_name_text,
        site_name_font,
        letter_spacing=site_name_letter_spacing,
        word_spacing=site_name_word_spacing,
        fill=site_name_color,
    )

    slogan_config = config["slogan"]
    slogan_font_path = get_font_path(
        slogan_config["font_family"],
        slogan_config["font_weight"],
        slogan_config["font_style"],
    )
    slogan_font = ImageFont.truetype(slogan_font_path, slogan_config["font_size"])
    slogan_color = tuple(
        int(slogan_config["color"][i : i + 2], 16) for i in (1, 3, 5)
    ) + (255,)
    slogan_position = (slogan_config["position"]["x"], slogan_config["position"]["y"])
    slogan_text = slogan_config["text"]
    slogan_letter_spacing = slogan_config.get("letter_spacing", 0)
    slogan_word_spacing = slogan_config.get("word_spacing", 0)

    draw_text_with_spacing(
        draw,
        slogan_position,
        slogan_text,
        slogan_font,
        letter_spacing=slogan_letter_spacing,
        word_spacing=slogan_word_spacing,
        fill=slogan_color,
    )

    output_path = "output.png"
    image.save(output_path, "PNG")
    return output_path
