import sys
import pandas as pd
import os
from jinja2 import Template
from concurrent.futures import ThreadPoolExecutor
from xml.etree import ElementTree as ET
import webbrowser
from tqdm import tqdm

def find_unique_patterns(input_csv, output_html_file="unique_patterns_page.html"):
    try:
        df = pd.read_csv(input_csv)
        if 'gse_id' not in df.columns:
            print("The CSV file must contain an 'gse_id' column.")
            sys.exit(1)
        gse_ids = df['gse_id'].unique()

        for gse_id in tqdm(gse_ids, desc="Finding Unique Patterns...", unit="Row", ncols=100):
            find_unique_pattern(gse_id)

        html_template = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Unique Patterns</title>
            <style>
                @page { size: A4; margin: 0; }
                body { font-family: Arial, sans-serif; margin: 0; padding: 0; }
                .qr-page { page-break-before: always; display: flex; flex-wrap: wrap; justify-content: space-between; }
                .qr-code { width: 47%; display: flex; justify-content: center; }
                .qr-code img { width: 100%; height: auto; }
                @media print { body { margin: 0; padding: 0; } .qr-page { page-break-before: always; } }
            </style>
        </head>
        <body>
            {% for i in range(0, unique_list|length, 6) %}
                <div class="unique-page">
                    {% for unique in unique_list[i:i+6] %}
                        <div class="unique-code">
                            <img src="{{ unique }}" alt="unique Code">
                        </div>
                    {% endfor %}
                </div>
            {% endfor %}
            <script>window.print()</script>
        </body>
        </html>
        """

        template = Template(html_template)
        html_output = template.render(unique_list=unique_list)

        with open(output_html_file, "w") as file:
            file.write(html_output)

        print(f"HTML file with Unique patterns generated: {output_html_file}")
        webbrowser.open('file://' + os.path.realpath(output_html_file))

    except Exception as e:
        print(f"Error generating HTML file: {e}")

def main():
    if len(sys.argv) != 2:
        print("Usage: python script.py <input_csv_file>")
        sys.exit(1)
    input_csv = sys.argv[1]
    find_unique_patterns(input_csv)

if __name__ == "__main__":
    main()
