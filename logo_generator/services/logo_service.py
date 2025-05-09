import base64
import json
import os

import svgwrite
from django.conf import settings
from logo_generator.utils.font_utils import get_font_path
from logo_generator.utils.image_utils import draw_text_with_spacing
from PIL import Image, ImageDraw, ImageFont


def generate_logo(config_path=None):
    """Generate a logo from a JSON configuration file."""
    if not config_path:
        config_path = settings.DEFAULT_CONFIG_PATH

    try:
        with open(config_path) as f:
            config = json.load(f)
    except FileNotFoundError:
        raise Exception(f"File not found: {config_path}")

    # Get output format from config, default to "png" if not specified
    output_format = config.get("output", "png").lower()

    # Check if auto-trim is enabled in the config
    auto_trim = config.get("auto_trim", False)

    output_path = ""
    if output_format == "svg":
        output_path = generate_svg_logo(config)
    else:
        output_path = generate_png_logo(config)

    # Auto-trim if specified in the config
    if auto_trim:
        from logo_force.trim_logo import trim_image

        filename, ext = os.path.splitext(output_path)
        trimmed_path = f"{filename}_trimmed{ext}"
        if trim_image(output_path, trimmed_path):
            return trimmed_path

    return output_path


def generate_png_logo(config):
    """Generate a PNG logo from the configuration."""
    # Create image with the specified dimensions
    image_width = config["image"]["width"]
    image_height = config["image"]["height"]
    image = Image.new("RGBA", (image_width, image_height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)

    # Set background if not transparent
    if config["image"]["background"] != "transparent":
        # Create a background rectangle
        background_color = config["image"]["background"]
        # Convert hex color to RGBA
        if background_color.startswith("#"):
            r = int(background_color[1:3], 16)
            g = int(background_color[3:5], 16)
            b = int(background_color[5:7], 16)
            background_color = (r, g, b, 255)

        # Fill the entire image with the background color
        bg_image = Image.new("RGBA", (image_width, image_height), background_color)
        # Paste the original image on top
        bg_image.paste(image, (0, 0), image)
        image = bg_image
        draw = ImageDraw.Draw(image)

    # Process site name
    site_name_config = config["site_name"]
    site_name_font_path = get_font_path(
        site_name_config["font_family"],
        site_name_config["font_weight"],
        site_name_config["font_style"],
    )

    # Create font with the specified size
    site_name_font_size = site_name_config["font_size"]
    site_name_font = ImageFont.truetype(site_name_font_path, site_name_font_size)

    # Store font family for adjustment in draw_text_with_spacing
    site_name_font.font_family = site_name_config["font_family"]

    # Convert hex color to RGBA
    site_name_color = tuple(
        int(site_name_config["color"][i : i + 2], 16) for i in (1, 3, 5)
    ) + (255,)

    # Get position from config
    site_name_position = (
        site_name_config["position"]["x"],
        site_name_config["position"]["y"],
    )

    # Get text and spacing settings
    site_name_text = site_name_config["text"]
    site_name_letter_spacing = site_name_config.get("letter_spacing", 0)
    site_name_word_spacing = site_name_config.get("word_spacing", 0)

    # Draw site name with proper spacing
    draw_text_with_spacing(
        draw,
        site_name_position,
        site_name_text,
        site_name_font,
        letter_spacing=site_name_letter_spacing,
        word_spacing=site_name_word_spacing,
        fill=site_name_color,
    )

    # Process slogan
    slogan_config = config["slogan"]
    slogan_font_path = get_font_path(
        slogan_config["font_family"],
        slogan_config["font_weight"],
        slogan_config["font_style"],
    )

    # Create font with the specified size
    slogan_font_size = slogan_config["font_size"]
    slogan_font = ImageFont.truetype(slogan_font_path, slogan_font_size)

    # Store font family for adjustment in draw_text_with_spacing
    slogan_font.font_family = slogan_config["font_family"]

    # Convert hex color to RGBA
    slogan_color = tuple(
        int(slogan_config["color"][i : i + 2], 16) for i in (1, 3, 5)
    ) + (255,)

    # Get position from config
    slogan_position = (slogan_config["position"]["x"], slogan_config["position"]["y"])

    # Get text and spacing settings
    slogan_text = slogan_config["text"]
    slogan_letter_spacing = slogan_config.get("letter_spacing", 0)
    slogan_word_spacing = slogan_config.get("word_spacing", 0)

    # Draw slogan with proper spacing
    draw_text_with_spacing(
        draw,
        slogan_position,
        slogan_text,
        slogan_font,
        letter_spacing=slogan_letter_spacing,
        word_spacing=slogan_word_spacing,
        fill=slogan_color,
    )

    # Save the PNG file
    output_path = "output.png"
    image.save(output_path, "PNG")
    return output_path


def generate_svg_logo(config):
    """Generate an SVG logo from the configuration."""
    image_width = config["image"]["width"]
    image_height = config["image"]["height"]

    # Create SVG drawing
    dwg = svgwrite.Drawing("output.svg", size=(image_width, image_height))

    # Get font families to include
    site_name_font_family = config["site_name"]["font_family"]
    slogan_font_family = config["slogan"]["font_family"]

    # Get SVG options
    svg_options = config.get("svg_options", {})
    embed_fonts = svg_options.get("embed_fonts", False)

    if embed_fonts:
        # Get font paths for embedding
        site_name_font_path = get_font_path(
            site_name_font_family,
            config["site_name"]["font_weight"],
            config["site_name"]["font_style"],
        )

        slogan_font_path = get_font_path(
            slogan_font_family,
            config["slogan"]["font_weight"],
            config["slogan"]["font_style"],
        )

        # Embed fonts as data URIs
        font_css = embed_fonts_as_css(
            [
                (site_name_font_family, site_name_font_path),
                (slogan_font_family, slogan_font_path),
            ]
        )

        style = dwg.style(font_css)
        dwg.defs.add(style)
    else:
        # Add Google Fonts import
        fonts_to_import = set([site_name_font_family, slogan_font_family])
        google_fonts_url = create_google_fonts_url(fonts_to_import)

        # Add style that imports Google Fonts
        style = dwg.style(
            f"""
            @import url('{google_fonts_url}');
        """
        )
        dwg.defs.add(style)

    # Set background if not transparent
    if config["image"]["background"] != "transparent":
        dwg.add(
            dwg.rect(
                insert=(0, 0), size=("100%", "100%"), fill=config["image"]["background"]
            )
        )

    # Process site name
    site_name_config = config["site_name"]
    site_name_text = site_name_config["text"]
    site_name_color = site_name_config["color"]
    site_name_position = (
        site_name_config["position"]["x"],
        site_name_config["position"]["y"],
    )
    site_name_font_family = site_name_config["font_family"]
    site_name_font_size = site_name_config["font_size"]
    site_name_letter_spacing = site_name_config.get("letter_spacing", 0)
    site_name_font_weight = site_name_config["font_weight"]
    site_name_font_style = site_name_config["font_style"]

    # Get font metrics from the actual font file
    site_name_font_path = get_font_path(
        site_name_font_family,
        site_name_font_weight,
        site_name_font_style,
    )

    # Add site name text with letter spacing
    site_name = dwg.text(
        "",
        insert=site_name_position,
        fill=site_name_color,
        font_family=f"'{site_name_font_family}'",  # Quote font family name
        font_size=site_name_font_size,
        font_weight=site_name_font_weight,
        font_style=site_name_font_style,
    )

    # Handle letter spacing for site name
    x_offset = 0
    for char in site_name_text:
        if char == " ":
            x_offset += site_name_config.get("word_spacing", site_name_letter_spacing)
        else:
            tspan = dwg.tspan(char, x=[site_name_position[0] + x_offset])
            site_name.add(tspan)
            # Use the actual font to calculate character width
            char_width = calculate_char_width(
                char, site_name_font_path, site_name_font_size
            )
            x_offset += char_width + site_name_letter_spacing

    dwg.add(site_name)

    # Process slogan
    slogan_config = config["slogan"]
    slogan_text = slogan_config["text"]
    slogan_color = slogan_config["color"]
    slogan_position = (
        slogan_config["position"]["x"],
        slogan_config["position"]["y"],
    )
    slogan_font_family = slogan_config["font_family"]
    slogan_font_size = slogan_config["font_size"]
    slogan_letter_spacing = slogan_config.get("letter_spacing", 0)
    slogan_font_weight = slogan_config["font_weight"]
    slogan_font_style = slogan_config["font_style"]

    # Get font metrics from the actual font file
    slogan_font_path = get_font_path(
        slogan_font_family,
        slogan_font_weight,
        slogan_font_style,
    )

    # Add slogan text with letter spacing
    slogan = dwg.text(
        "",
        insert=slogan_position,
        fill=slogan_color,
        font_family=f"'{slogan_font_family}'",  # Quote font family name
        font_size=slogan_font_size,
        font_weight=slogan_font_weight,
        font_style=slogan_font_style,
    )

    # Handle letter spacing for slogan
    x_offset = 0
    for char in slogan_text:
        if char == " ":
            x_offset += slogan_config.get("word_spacing", slogan_letter_spacing)
        else:
            tspan = dwg.tspan(char, x=[slogan_position[0] + x_offset])
            slogan.add(tspan)
            # Use the actual font to calculate character width
            char_width = calculate_char_width(char, slogan_font_path, slogan_font_size)
            x_offset += char_width + slogan_letter_spacing

    dwg.add(slogan)

    # Save the SVG file
    dwg.save()
    return "output.svg"


def create_google_fonts_url(font_families):
    """Create a Google Fonts URL for the specified font families."""
    # Format: https://fonts.googleapis.com/css2?family=Font+Name:wght@400;700&family=Another+Font:ital,wght@0,400;1,700
    base_url = "https://fonts.googleapis.com/css2"
    formatted_families = []

    for family in font_families:
        # Replace spaces with + for URL format
        formatted_family = family.replace(" ", "+")
        formatted_families.append(f"family={formatted_family}")

    return f"{base_url}?{'&'.join(formatted_families)}&display=swap"


def calculate_char_width(char, font_path, font_size):
    """Calculate character width using the actual font file."""
    try:
        # Use PIL's ImageFont to get character width
        font = ImageFont.truetype(font_path, font_size)
        return font.getlength(char)
    except Exception:
        # Fallback to approximation if there's an error
        return font_size * 0.6  # Rough estimate


def embed_fonts_as_css(font_list):
    """
    Embed fonts as data URIs in CSS.

    Args:
        font_list: List of tuples (font_family, font_path)

    Returns:
        CSS string with embedded fonts
    """
    css = []

    for font_family, font_path in font_list:
        try:
            with open(font_path, "rb") as f:
                font_data = f.read()

            # Encode font as base64
            encoded_font = base64.b64encode(font_data).decode("utf-8")

            # Determine font format from file extension
            font_format = os.path.splitext(font_path)[1].lower().replace(".", "")
            if font_format == "ttf":
                font_format = "truetype"

            # Create @font-face rule
            css.append(
                f"""
@font-face {{
    font-family: '{font_family}';
    src: url('data:font/{font_format};base64,{encoded_font}') format('{font_format}');
    font-weight: normal;
    font-style: normal;
}}
            """
            )
        except Exception as e:
            # If embedding fails, log error and continue
            print(f"Error embedding font {font_family}: {str(e)}")

    return "\n".join(css)
