import os
import sys
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import qrcode
from tqdm import tqdm

# npm install -g nodemon
# nodemon --watch qrgen.py --watch ../api/database.csv --exec "python qrgen.py ../api/database.csv"

def mm_to_pixels(mm, dpi=300):
    pixels = int((mm / 25.4) * dpi)
    if mm == 140:
        pixels += 1
    return pixels

def generate_qr_code_with_label(gse_id_value, old_gse_id_value, output_dir="../qr_codes"):
    try:
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        gse_id_value = str(gse_id_value)
        old_gse_id_value = str(old_gse_id_value)
        qr = qrcode.QRCode(
            version=10,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=16,
            border=2,
        )
        qr.add_data(gse_id_value)
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white").convert("RGB")
        label_width = mm_to_pixels(140)
        label_height = mm_to_pixels(40)
        canvas = Image.new("RGB", (label_width, label_height), "white")
        qr_img = qr_img.resize((label_height, label_height), Image.Resampling.LANCZOS)
        canvas.paste(qr_img, (0, 0))
        try:
            font = ImageFont.truetype("arial.ttf", size=190)
        except IOError:
            font = ImageFont.load_default()
        draw = ImageDraw.Draw(canvas)
        label1_bbox = draw.textbbox((0, 0), gse_id_value, font=font)
        draw.text((label_height + 20, 20), gse_id_value, fill="black", font=font)
        line_y = label1_bbox[3] + 40
        draw.line([(label_height + 20, line_y), (label_width, line_y)], fill="black", width=5)
        draw.text((label_height + 20, line_y), old_gse_id_value, fill="black", font=font)
        output_path = os.path.join(output_dir, f"{gse_id_value}.png")
        canvas.save(output_path, "PNG")
    except Exception as e:
        print(f"Error generating QR Code for {gse_id_value}: {e}")

def generate_qr_codes_from_csv(input_csv):
    try:
        df = pd.read_csv(input_csv)
        if 'gse_id' not in df.columns or 'old_gse_id' not in df.columns:
            print("The CSV file must contain 'gse_id' and 'old_gse_id' columns.")
            sys.exit(1)
        gse_ids = df[['gse_id', 'old_gse_id']].drop_duplicates()
        for _, row in tqdm(gse_ids.iterrows(), desc="Generating QR codes", unit="QR", ncols=100):
            gse_id = row['gse_id']
            old_gse_id = row['old_gse_id']
            generate_qr_code_with_label(gse_id, old_gse_id)
        print("QR code generation complete.")
    except Exception as e:
        print(f"Error processing CSV file: {e}")

def main():
    if len(sys.argv) != 2:
        print("Usage: python script.py <input_csv_file>")
        sys.exit(1)

    input_csv = sys.argv[1]
    generate_qr_codes_from_csv(input_csv)

if __name__ == "__main__":
    main()
