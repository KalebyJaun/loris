import pytesseract

def extract_text_with_ocr(image_path: str) -> str:
    return process_ocr_output(pytesseract.image_to_string(image_path))

def process_ocr_output(ocr_text: str) -> str:
    return ocr_text.replace(",  ", ".").replace("$", "").replace("RG", "R$")