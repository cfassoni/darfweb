import os
import pdfplumber
from datetime import datetime


def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extracts all text from the PDF to a single string.
    """
    # print(f"📄 Extracting text from {pdf_path}...")
    filename = os.path.basename(pdf_path)
    extract_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    text = f"--- FILE: {filename}\n--- EXTRACTED AT: {extract_date}\n\n"
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages):
            page_text = page.extract_text()
            if page_text:
                text += f"--- PAGE {i + 1} ---\n{page_text}\n"
    return text
