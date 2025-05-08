from PIL import Image


def trim_image(input_path, output_path):
    image = Image.open(input_path)
    # Convert to RGBA mode if not already
    if image.mode != "RGBA":
        image = image.convert("RGBA")

    # Find bounding box of non-transparent content
    bbox = image.getbbox()
    if bbox:
        # Crop image according to bounding box
        cropped_image = image.crop(bbox)
        cropped_image.save(output_path, "PNG")
        print(f"Image has been trimmed and saved at: {output_path}")
    else:
        print("No content found to trim")


if __name__ == "__main__":
    trim_image("output.png", "output_trimmed.png")
