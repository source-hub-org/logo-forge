import logging

from PIL import Image, ImageDraw

logger = logging.getLogger(__name__)


def draw_text_with_spacing(
    draw, xy, text, font, letter_spacing=0, word_spacing=0, fill=(0, 0, 0, 255)
):
    """Vẽ văn bản với khoảng cách chữ và từ tùy chỉnh."""
    x, y = xy
    logger.debug(
        f"Vẽ văn bản: '{text}' tại ({x}, {y}) "
            + "với letter_spacing={letter_spacing}, word_spacing={word_spacing}"
    )

    for i, char in enumerate(text):
        draw.text((x, y), char, font=font, fill=fill)
        char_width = font.getlength(char)

        # Mặc định sử dụng letter_spacing
        spacing = letter_spacing

        # Nếu ký tự hiện tại là dấu cách,
        # sử dụng word_spacing cho khoảng cách đến ký tự tiếp theo
        if char == " ":
            spacing = word_spacing
            logger.debug(
                f"Áp dụng word_spacing={word_spacing} cho dấu cách tại vị trí {i}"
            )

        x += char_width + spacing
        logger.debug(f"Ký tự '{char}' tại x={x}, width={char_width}, spacing={spacing}")


def create_logo_image(config):
    """Tạo ảnh logo từ cấu hình JSON."""
    image_width = config["image"]["width"]
    image_height = config["image"]["height"]
    image = Image.new("RGBA", (image_width, image_height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    return image, draw
