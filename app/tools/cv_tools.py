import pytesseract

def extract_text_with_ocr(image_path: str) -> str:
    return pytesseract.image_to_string(image_path)