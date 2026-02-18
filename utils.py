# Utility Functions for PDF Generation and Data Processing

import pdfkit
import pandas as pd


def generate_pdf_from_dataframe(df, output_path):
    """Generates a PDF file from a given DataFrame."""
    html = df.to_html()  # Convert DataFrame to HTML
    pdfkit.from_string(html, output_path)  # Convert HTML to PDF

def process_data(input_file, output_file):
    """Reads data from a CSV file, processes it, and saves it to a new CSV file."""
    df = pd.read_csv(input_file)  # Read CSV file
    # Perform data processing here, e.g., cleaning, filtering
    df.to_csv(output_file, index=False)  # Save processed data to new CSV file
