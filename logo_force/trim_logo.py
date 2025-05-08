from PIL import Image


def trim_image(input_path, output_path):
    image = Image.open(input_path)
    # Chuyển về chế độ RGBA nếu chưa phải
    if image.mode != "RGBA":
        image = image.convert("RGBA")

    # Tìm bounding box của phần không trong suốt
    bbox = image.getbbox()
    if bbox:
        # Cắt ảnh theo bounding box
        cropped_image = image.crop(bbox)
        cropped_image.save(output_path, "PNG")
        print(f"Ảnh đã được trim và lưu tại: {output_path}")
    else:
        print("Không tìm thấy nội dung để trim")


if __name__ == "__main__":
    trim_image("output.png", "output_trimmed.png")
