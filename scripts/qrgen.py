# python qrgen.py ../api/database.csv ./logo.png ./star.png

import os
import sys
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import qrcode
from tqdm import tqdm
from qrcode.image.styledpil import StyledPilImage

def mm_to_pixels(mm, dpi=300):
    pixels = int((mm / 25.4) * dpi)
    if mm == 140:
        pixels += 1
    return pixels

def resize_logo(logo_path):
    try:
        logo = Image.open(logo_path).convert("RGBA")
        logo_resized = logo.point(lambda p: 0 if p < 128 else 255)
        logo_resized = logo_resized.convert("RGBA")
        logo_width, logo_height = logo_resized.size
        logo_resized = logo_resized.resize((logo_width // 3, logo_height // 3))
        return logo_resized
    except Exception as e:
        print(f"Error converting logo to black: {e}")
        return None

def generate_qr_code_with_label(gse_id_value, old_gse_id_value, logo_resized, embed_logo_path, output_dir="./qr_codes"):
    try:
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        gse_id_value = str(gse_id_value)
        old_gse_id_value = str(old_gse_id_value)
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=16,
            border=2,
        )
        qr.add_data(gse_id_value)
        qr.make(fit=True)
        qr_img = qr.make_image(image_factory=StyledPilImage, embeded_image_path=embed_logo_path if embed_logo_path else None, fill_color="black", back_color="white").convert("RGB")
        label_width = mm_to_pixels(140)
        label_height = mm_to_pixels(65)
        canvas = Image.new("RGB", (label_width, label_height), "white")
        qr_img = qr_img.resize((label_height, label_height), Image.Resampling.LANCZOS)
        canvas.paste(qr_img, (0, 0))

        padding = 20
        text_x = label_height + padding
        text_area_w = label_width - text_x - padding
        # Each of the two text lines gets ~half the canvas height minus padding
        text_area_h = (label_height // 2) - padding

        script_dir = os.path.dirname(os.path.abspath(__file__))
        font_path = os.path.join(script_dir, "..", "fonts", "arial.ttf")
        font = ImageFont.load_default()
        draw = ImageDraw.Draw(canvas)
        for size in range(600, 10, -2):
            try:
                candidate = ImageFont.truetype(font_path, size=size)
            except IOError:
                print(f"Font not found at {font_path}, using default font")
                break
            bb1 = draw.textbbox((0, 0), gse_id_value, font=candidate)
            bb2 = draw.textbbox((0, 0), old_gse_id_value, font=candidate)
            w1, h1 = bb1[2] - bb1[0], bb1[3] - bb1[1]
            w2, h2 = bb2[2] - bb2[0], bb2[3] - bb2[1]
            if w1 <= text_area_w and h1 <= text_area_h and w2 <= text_area_w and h2 <= text_area_h:
                font = candidate
                break

        label1_bbox = draw.textbbox((0, 0), gse_id_value, font=font)
        line1_h = label1_bbox[3] - label1_bbox[1]
        y1 = (label_height // 2 - line1_h) // 2
        draw.text((text_x, y1), gse_id_value, fill="black", font=font)

        line_y = label_height // 2
        draw.line([(text_x, line_y), (label_width - padding, line_y)], fill="black", width=5)

        label2_bbox = draw.textbbox((0, 0), old_gse_id_value, font=font)
        line2_h = label2_bbox[3] - label2_bbox[1]
        y2 = line_y + (label_height // 2 - line2_h) // 2
        draw.text((text_x, y2), old_gse_id_value, fill="black", font=font)

        logo_width, logo_height = logo_resized.size
        canvas_width, canvas_height = canvas.size
        logo_position = (canvas_width - logo_width - 20, canvas_height - logo_height - 20)
        canvas.paste(logo_resized, logo_position, logo_resized)

        output_path = os.path.join(output_dir, f"{gse_id_value}.png")
        canvas.save(output_path, "PNG")
    except Exception as e:
        print(f"Error generating QR Code for {gse_id_value}: {e}")

def generate_qr_codes_from_csv(input_csv, logo_resized, embed_logo_path):
    try:
        df = pd.read_csv(input_csv)
        if 'gse_id' not in df.columns or 'old_gse_id' not in df.columns:
            print("The CSV file must contain 'gse_id' and 'old_gse_id' columns.")
            sys.exit(1)
        gse_ids = df[['gse_id', 'old_gse_id']].drop_duplicates()
        for _, row in tqdm(gse_ids.iterrows(), desc="Generating QR codes", unit="QR", ncols=100):
            gse_id = row['gse_id']
            old_gse_id = row['old_gse_id']
            generate_qr_code_with_label(gse_id, old_gse_id, logo_resized, embed_logo_path)
        print("QR code generation complete.")
    except Exception as e:
        print(f"Error processing CSV file: {e}")

def main():
    if len(sys.argv) not in (3, 4):
        print("Usage: python script.py <input_csv_file> <logo_path> [embed_logo_path]")
        sys.exit(1)

    input_csv = sys.argv[1]
    logo_path = sys.argv[2]
    embed_logo_path = sys.argv[3] if len(sys.argv) == 4 else None

    if not os.path.exists(logo_path):
        print(f"❌ Logo file not found: {logo_path}")
        sys.exit(1)

    if embed_logo_path and not os.path.exists(embed_logo_path):
        print(f"❌ Embed logo file not found: {embed_logo_path}")
        sys.exit(1)

    logo_resized = resize_logo(logo_path)

    if logo_resized is None:
        print("❌ Failed to load and convert logo to black. Exiting.")
        sys.exit(1)

    generate_qr_codes_from_csv(input_csv, logo_resized, embed_logo_path)

if __name__ == "__main__":
    main()
