import sys
import pandas as pd
import os
from jinja2 import Template
from concurrent.futures import ThreadPoolExecutor
import qrcode
import qrcode.image.svg
from xml.etree import ElementTree as ET

method = 'basic'

if method == 'basic':
    factory = qrcode.image.svg.SvgImage
elif method == 'fragment':
    factory = qrcode.image.svg.SvgFragmentImage
elif method == 'bg1':
    factory = qrcode.image.svg.SvgFillImage
elif method == 'bg2':
    factory = qrcode.image.svg.SvgPathFillImage
else:
    factory = qrcode.image.svg.SvgPathImage

def fix_svg_namespace(svg_file_path):
    try:
        with open(svg_file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        content = content.replace('svg:rect', 'rect')
        content = content.replace('svg:svg', 'svg')
        content = content.replace('xmlns:svg', 'xmlns')
        with open(svg_file_path, 'w', encoding='utf-8') as file:
            file.write(content)
        print(f"Fixed file: {svg_file_path}")
    except Exception as e:
        print(f"Error fixing file {svg_file_path}: {e}")

def generate_qr_code_with_label(gse_id_value, output_dir="../qr_codes"):
    try:
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # Increase box_size for better quality (300 DPI)
        qr = qrcode.make(str(gse_id_value),
                         image_factory=factory,
                         error_correction=qrcode.constants.ERROR_CORRECT_H,
                         border=4,
                         box_size=30)  # Adjusted for print quality

        qr_file_path = os.path.join(output_dir, f"{gse_id_value}.svg")
        qr.save(qr_file_path)
        tree = ET.parse(qr_file_path)
        root = tree.getroot()

        # Center the label at the top
        label = ET.Element('text', {
            'x': '50%',  # Center horizontally
            'y': '40',   # Position label just above the QR code
            'text-anchor': 'middle',
            'font-size': '30',  # Adjust font size for better visibility
            'font-family': 'Arial-Bold',  # Use a bold font
            'fill': 'black'
        })
        label.text = gse_id_value
        root.append(label)
        tree.write(qr_file_path)
        fix_svg_namespace(qr_file_path)
        print(f"QR Code with label generated for gse_id: {gse_id_value}")
    except Exception as e:
        print(f"Error generating QR Code for gse_id {gse_id_value}: {e}")

def generate_html(input_csv, output_html_file="qr_codes_page.html"):
    try:
        df = pd.read_csv(input_csv)
        if 'gse_id' not in df.columns:
            print("The CSV file must contain an 'gse_id' column.")
            sys.exit(1)
        gse_ids = df['gse_id'].unique()

        # Generate QR codes
        for gse_id in gse_ids:
            generate_qr_code_with_label(gse_id)

        # Create HTML with embedded QR codes
        qr_images = []
        for gse_id in gse_ids:
            qr_images.append(f"../qr_codes/{gse_id}.svg")

        # Load template and generate HTML
        html_template = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>QR Codes</title>
            <style>
                @page {
                    size: A4;
                    margin: 0;
                }
                body {
                    font-family: Arial, sans-serif;
                    margin: 0;
                    padding: 0;
                }
                .qr-page {
                    page-break-before: always;
                    display: flex;
                    flex-wrap: wrap;
                    justify-content: space-between;
                }
                .qr-code {
                    width: 47%;
                    margin-bottom: 10px;
                    display: flex;
                    justify-content: center;
                }
                .qr-code img {
                    width: 100%;
                    height: auto;
                }
                @media print {
                    body {
                        margin: 0;
                        padding: 0;
                    }
                    .qr-page {
                        page-break-before: always;
                    }
                }
            </style>
        </head>
        <body>
            {% for i in range(0, qr_images|length, 6) %}
                <div class="qr-page">
                    {% for qr in qr_images[i:i+6] %}
                        <div class="qr-code">
                            <img src="{{ qr }}" alt="QR Code">
                        </div>
                    {% endfor %}
                </div>
            {% endfor %}
            <script>window.print()</script>
        </body>
        </html>
        """

        template = Template(html_template)
        html_output = template.render(qr_images=qr_images)

        # Write to HTML file
        with open(output_html_file, "w") as file:
            file.write(html_output)

        print(f"HTML file with QR codes generated: {output_html_file}")

    except Exception as e:
        print(f"Error generating HTML file: {e}")

def main():
    if len(sys.argv) != 2:
        print("Usage: python script.py <input_csv_file>")
        sys.exit(1)
    input_csv = sys.argv[1]
    generate_html(input_csv)

if __name__ == "__main__":
    main()
