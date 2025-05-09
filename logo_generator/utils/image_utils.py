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
        + f"with letter_spacing={letter_spacing}, word_spacing={word_spacing}"
    )

    # Calculate text metrics for proper vertical alignment
    # Get the ascent and descent of the font
    try:
        # For newer versions of Pillow
        ascent, descent = font.getmetrics()
    except AttributeError:
        try:
            # Fallback for older versions
            ascent = font.getsize("A")[1]
            descent = 0
        except:
            # Last resort fallback
            ascent = font.size
            descent = 0

    # Adjust y position to match SVG text positioning
    # In SVG, text y-coordinate is at the baseline
    # In PIL, text y-coordinate is at the top
    # We need to adjust y by adding the ascent

    # Different font families need different adjustment factors
    # Script fonts like "Mrs Sheppards" need more adjustment
    font_family = getattr(font, "font_family", "").lower()
    adjustment_factor = 0.8  # Default adjustment factor

    if "script" in font_family or "sheppards" in font_family:
        adjustment_factor = 0.9
    elif "dots" in font_family or "zen" in font_family:
        adjustment_factor = 0.75

    # Calculate the adjusted y position
    adjusted_y = y - (ascent * adjustment_factor)

    # Store the original x for debugging
    original_x = x

    # Draw each character with proper spacing
    for i, char in enumerate(text):
        # Draw the character
        draw.text((x, adjusted_y), char, font=font, fill=fill)

        # Get character width
        try:
            # For newer versions of Pillow
            char_width = font.getlength(char)
        except AttributeError:
            try:
                # Fallback for older versions
                char_width = font.getsize(char)[0]
            except:
                # Last resort fallback
                char_width = font.size * 0.6

        # Adjust character width for specific characters
        if char in "mwWM":
            char_width *= 1.2  # Wider characters
        elif char in "il1":
            char_width *= 0.8  # Narrower characters

        # Default to letter_spacing
        spacing = letter_spacing

        # If current character is a space, use word_spacing for the distance to the next character
        if char == " ":
            spacing = word_spacing
            logger.debug(
                f"Applying word_spacing={word_spacing} for space at position {i}"
            )

        # Move to the next character position
        x += char_width + spacing

        logger.debug(
            f"Character '{char}' at x={x}, width={char_width}, spacing={spacing}"
        )

    # Log the total width for debugging
    logger.debug(f"Total text width: {x - original_x} pixels")


def create_logo_image(config):
    """Create logo image from JSON configuration."""
    image_width = config["image"]["width"]
    image_height = config["image"]["height"]
    image = Image.new("RGBA", (image_width, image_height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    return image, draw
