import fitz

def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    extracted = []

    for page_number in range(len(doc)):
        page = doc.load_page(page_number)
        text = page.get_text()

        if text.strip():
            extracted.append({
                "page_number": page_number + 1,
                "text": text
            })

    doc.close()
    return extracted