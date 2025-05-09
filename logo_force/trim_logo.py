import os
import re
import xml.etree.ElementTree as ET

from PIL import Image


def trim_png_image(input_path, output_path):
    """Trim transparent space from a PNG image."""
    image = Image.open(input_path)
    # Convert to RGBA mode if not already
    if image.mode != "RGBA":
        image = image.convert("RGBA")

    # Find bounding box of non-transparent content
    bbox = image.getbbox()
    if bbox:
        # Get the bounding box coordinates
        left, top, right, bottom = bbox

        # Add padding to match SVG padding
        padding = 20
        left = max(0, left - padding)
        top = max(0, top - padding)
        right = min(image.width, right + padding)
        bottom = min(image.height, bottom + padding)

        # Crop image according to bounding box with padding
        cropped_image = image.crop((left, top, right, bottom))

        # Generate the SVG file if it doesn't exist yet
        svg_path = input_path.replace(".png", ".svg")
        svg_trimmed_path = output_path.replace(".png", ".svg")

        if not os.path.exists(svg_trimmed_path) and os.path.exists(svg_path):
            # Generate the trimmed SVG first
            trim_svg_image(svg_path, svg_trimmed_path)

        # Get dimensions from the trimmed SVG file if it exists
        if os.path.exists(svg_trimmed_path):
            try:
                # Try to get SVG dimensions for consistency
                tree = ET.parse(svg_trimmed_path)
                root = tree.getroot()
                svg_width = float(root.get("width", 0))
                svg_height = float(root.get("height", 0))

                # If SVG dimensions are valid
                if svg_width > 0 and svg_height > 0:
                    # Calculate the aspect ratio of the cropped PNG
                    png_width, png_height = cropped_image.size
                    png_aspect = png_width / png_height

                    # Calculate the aspect ratio of the SVG
                    svg_aspect = svg_width / svg_height

                    # Determine the new dimensions to match the SVG aspect ratio
                    if (
                        abs(png_aspect - svg_aspect) > 0.1
                    ):  # If aspect ratios differ significantly
                        # Use the SVG dimensions directly
                        new_width = int(svg_width)
                        new_height = int(svg_height)
                    else:
                        # Maintain PNG dimensions but adjust to match SVG aspect ratio
                        if png_width > png_height:
                            new_width = png_width
                            new_height = int(png_width / svg_aspect)
                        else:
                            new_height = png_height
                            new_width = int(png_height * svg_aspect)

                    # Resize PNG to match the calculated dimensions
                    cropped_image = cropped_image.resize(
                        (new_width, new_height), Image.LANCZOS
                    )
                    print(
                        f"Resized PNG to match SVG aspect ratio: {new_width}x{new_height}"
                    )
            except Exception as e:
                print(f"Could not match SVG dimensions: {str(e)}")

        # Save the cropped image
        cropped_image.save(output_path, "PNG")
        print(f"PNG image has been trimmed and saved at: {output_path}")
        return True
    else:
        print("No content found to trim in PNG image")
        return False


def trim_svg_image(input_path, output_path):
    """Trim SVG by calculating the bounding box of all elements and updating viewBox."""
    try:
        # Read the SVG file
        with open(input_path) as f:
            svg_content = f.read()

        # Check if the SVG uses Google Fonts
        uses_google_fonts = (
            "@import url(" in svg_content and "fonts.googleapis.com" in svg_content
        )

        # Use ElementTree for reliable SVG parsing
        tree = ET.parse(input_path)
        root = tree.getroot()

        # Get all text elements and their tspans
        text_elements = []
        tspan_elements = []

        # Define SVG namespace
        ns = {"svg": "http://www.w3.org/2000/svg"}

        # First, try with namespace
        texts = root.findall(".//svg:text", ns)

        # If no texts found, try without namespace
        if not texts:
            texts = root.findall(".//text")

        # Process all text elements
        for text in texts:
            # Get text attributes
            try:
                x = float(text.get("x", "0"))
                y = float(text.get("y", "0"))
                font_size = float(text.get("font-size", "12"))
                font_family = text.get("font-family", "").strip("'\"")

                text_elements.append((x, y, font_size, font_family))

                # Find all tspans within this text element
                tspans = text.findall(".//tspan") or []

                for tspan in tspans:
                    try:
                        tspan_x = float(tspan.get("x", "0"))
                        tspan_text = tspan.text or ""
                        tspan_elements.append(
                            (tspan_x, tspan_text, font_size, font_family)
                        )
                    except (ValueError, TypeError):
                        continue
            except (ValueError, TypeError):
                continue

        # If ElementTree didn't find elements, use regex as fallback
        if not tspan_elements:
            tspan_pattern = r'<tspan x="([^"]*)"[^>]*>([^<]*)</tspan>'
            for match in re.finditer(tspan_pattern, svg_content):
                try:
                    x = float(match.group(1))
                    text = match.group(2)
                    # Use a default font size if not found
                    tspan_elements.append((x, text, 12, ""))
                except (ValueError, TypeError):
                    continue

        if not text_elements and not tspan_elements:
            print("Could not find any text or tspan elements in the SVG")
            return False

        print(
            f"Found {len(text_elements)} text elements and {len(tspan_elements)} tspan elements"
        )

        # Extract letter spacing and font information from the SVG content
        letter_spacing_pattern = r'letter-spacing="([^"]*)"'
        letter_spacing_match = re.search(letter_spacing_pattern, svg_content)
        letter_spacing = (
            float(letter_spacing_match.group(1)) if letter_spacing_match else 0
        )

        # Calculate the bounding box
        min_x = float("inf")
        max_x = float("-inf")
        min_y = float("inf")
        max_y = float("-inf")

        # Process text elements for y-coordinates
        for x, y, font_size, _ in text_elements:
            min_x = min(min_x, x)
            min_y = min(
                min_y, y - font_size
            )  # Text baseline is at y, so subtract font size for top
            max_y = max(max_y, y + font_size * 0.3)  # Add a bit for descenders

        # Extract font information from the config file to get accurate metrics
        config_path = None
        try:
            import json

            from django.conf import settings

            config_path = settings.DEFAULT_CONFIG_PATH
        except (ImportError, AttributeError):
            # If we can't import Django settings, try the default location
            config_path = os.path.join(
                os.path.dirname(os.path.dirname(input_path)), "default.json"
            )

        config = None
        if os.path.exists(config_path):
            try:
                with open(config_path) as f:
                    config = json.load(f)
            except:
                pass

        # Process tspan elements for x-coordinates and width
        for x, text, font_size, font_family in tspan_elements:
            min_x = min(min_x, x)

            # Adjust width calculation based on font family
            # Google Fonts tend to render differently than the default estimation
            width_multiplier = 0.6  # Default multiplier

            # If using Google Fonts, adjust the multiplier based on the font family
            if uses_google_fonts:
                # These are approximate multipliers for common Google Fonts
                # Adjust based on the specific fonts you're using
                if font_family and "script" in font_family.lower():
                    width_multiplier = 0.7  # Script fonts tend to be wider
                elif font_family and (
                    "condensed" in font_family.lower()
                    or "narrow" in font_family.lower()
                ):
                    width_multiplier = 0.5  # Condensed fonts are narrower
                elif font_family and (
                    "wide" in font_family.lower() or "expanded" in font_family.lower()
                ):
                    width_multiplier = 0.8  # Wide fonts are wider
                else:
                    # For Google Fonts, we need a more generous multiplier
                    width_multiplier = 0.65

                # If we have the config, use the actual font family information
                if config:
                    site_name_font = config.get("site_name", {}).get("font_family", "")
                    slogan_font = config.get("slogan", {}).get("font_family", "")

                    # Further adjust based on specific fonts in the config
                    if font_family and (
                        site_name_font.lower() in font_family.lower()
                        or font_family.lower() in site_name_font.lower()
                    ):
                        # For site name, use a more generous multiplier for Google Fonts
                        width_multiplier = 0.75
                        # Add extra for letter spacing
                        letter_spacing = max(
                            letter_spacing,
                            config.get("site_name", {}).get("letter_spacing", 0),
                        )

            # Calculate the end position of this tspan
            # Include letter spacing between characters
            char_width = font_size * width_multiplier

            # For Google Fonts, we need to be more generous with the width calculation
            if uses_google_fonts:
                # Add extra width for certain characters that tend to be wider
                for char in text:
                    if char in "mwWM":
                        char_width = font_size * 0.9  # Wider characters

            text_width = len(text) * char_width + (len(text) - 1) * letter_spacing
            end_x = x + text_width

            max_x = max(max_x, end_x)

        # If we couldn't find valid bounds, use defaults
        if min_x == float("inf") or min_y == float("inf"):
            min_x = 0
            min_y = 0

        if max_x == float("-inf") or max_y == float("-inf"):
            # Get dimensions from the SVG tag
            try:
                width = float(root.get("width", "800"))
                height = float(root.get("height", "600"))
                max_x = width
                max_y = height
            except (ValueError, TypeError):
                max_x = 800  # Default width
                max_y = 600  # Default height

        print(f"Calculated bounds: ({min_x}, {min_y}) to ({max_x}, {max_y})")

        # Add extra padding for Google Fonts to account for rendering differences
        padding = 20
        if uses_google_fonts:
            padding = 40  # More generous padding for Google Fonts

        min_x = max(0, min_x - padding)
        min_y = max(0, min_y - padding)
        max_x = max_x + padding
        max_y = max_y + padding

        # For Google Fonts, add extra width to ensure text isn't cut off
        if uses_google_fonts:
            # Add 20% extra width for Google Fonts
            extra_width = (max_x - min_x) * 0.2
            max_x += extra_width

        # Calculate new dimensions
        width = max_x - min_x
        height = max_y - min_y

        # Update the SVG attributes
        # First, find the SVG opening tag
        svg_start = svg_content.find("<svg")
        svg_end = svg_content.find(">", svg_start)

        if svg_start >= 0 and svg_end > svg_start:
            # Extract the SVG tag
            svg_tag = svg_content[svg_start : svg_end + 1]

            # Create new viewBox attribute
            viewbox = f"{min_x} {min_y} {width} {height}"

            # Create a new SVG tag with updated attributes
            new_svg_tag = svg_tag

            # Update width and height
            new_svg_tag = re.sub(r'width="[^"]*"', f'width="{width}"', new_svg_tag)
            new_svg_tag = re.sub(r'height="[^"]*"', f'height="{height}"', new_svg_tag)

            # Update or add viewBox
            if "viewBox" in new_svg_tag:
                new_svg_tag = re.sub(
                    r'viewBox="[^"]*"', f'viewBox="{viewbox}"', new_svg_tag
                )
            else:
                new_svg_tag = new_svg_tag.replace("<svg", f'<svg viewBox="{viewbox}"')

            # Replace the old SVG tag with the new one
            svg_content = svg_content.replace(svg_tag, new_svg_tag)

            # Write the updated SVG
            with open(output_path, "w") as f:
                f.write(svg_content)

            print(f"SVG image has been trimmed and saved at: {output_path}")
            return True
        else:
            print("Could not find SVG tag to update")
            return False

    except Exception as e:
        print(f"Error trimming SVG: {str(e)}")
        return False


def trim_image(input_path, output_path=None):
    """Trim an image file (PNG or SVG) to remove excess space."""
    if not output_path:
        # Generate output path based on input path
        filename, ext = os.path.splitext(input_path)
        output_path = f"{filename}_trimmed{ext}"

    # Determine file type based on extension
    _, ext = os.path.splitext(input_path.lower())

    # Check if both PNG and SVG versions exist
    base_path = os.path.splitext(input_path)[0]
    svg_exists = os.path.exists(f"{base_path}.svg")
    png_exists = os.path.exists(f"{base_path}.png")

    # If both formats exist, process SVG first to ensure consistent dimensions
    if ext == ".png" and svg_exists:
        svg_input = f"{base_path}.svg"
        svg_output = os.path.splitext(output_path)[0] + ".svg"
        # Process SVG first
        trim_svg_image(svg_input, svg_output)
        # Then process PNG
        return trim_png_image(input_path, output_path)
    elif ext == ".svg" and png_exists:
        # Process SVG
        result = trim_svg_image(input_path, output_path)
        # Then process PNG to match SVG dimensions
        png_input = f"{base_path}.png"
        png_output = os.path.splitext(output_path)[0] + ".png"
        trim_png_image(png_input, png_output)
        return result
    elif ext == ".png":
        return trim_png_image(input_path, output_path)
    elif ext == ".svg":
        return trim_svg_image(input_path, output_path)
    else:
        print(f"Unsupported file format: {ext}. Only PNG and SVG are supported.")
        return False


if __name__ == "__main__":
    # Check if output.png exists
    if os.path.exists("output.png"):
        trim_image("output.png", "output_trimmed.png")

    # Check if output.svg exists
    if os.path.exists("output.svg"):
        trim_image("output.svg", "output_trimmed.svg")
