import sys
from PyPDF2 import PdfReader


def extract_text_from_pdf(pdf_path):
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python extractor.py <pdf_file>")
        sys.exit(1)

    pdf_file = sys.argv[1]
    extracted_text = extract_text_from_pdf(pdf_file)
    print(extracted_text)
