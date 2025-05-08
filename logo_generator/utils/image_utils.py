import logging

from PIL import Image, ImageDraw

logger = logging.getLogger(__name__)


def draw_text_with_spacing(
    draw, xy, text, font, letter_spacing=0, word_spacing=0, fill=(0, 0, 0, 255)
):
    """Draw text with customized letter and word spacing."""
    x, y = xy
    logger.debug(
        f"Drawing text: '{text}' at ({x}, {y}) "
        + "with letter_spacing={letter_spacing}, word_spacing={word_spacing}"
    )

    for i, char in enumerate(text):
        draw.text((x, y), char, font=font, fill=fill)
        char_width = font.getlength(char)

        # Default to letter_spacing
        spacing = letter_spacing

        # If current character is a space, use word_spacing for the distance to the next character
        if char == " ":
            spacing = word_spacing
            logger.debug(
                f"Applying word_spacing={word_spacing} for space at position {i}"
            )

        x += char_width + spacing
        logger.debug(
            f"Character '{char}' at x={x}, width={char_width}, spacing={spacing}"
        )


def create_logo_image(config):
    """Create logo image from JSON configuration."""
    image_width = config["image"]["width"]
    image_height = config["image"]["height"]
    image = Image.new("RGBA", (image_width, image_height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    return image, draw
