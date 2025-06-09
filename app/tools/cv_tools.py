import pytesseract
from ollama_ocr import OCRProcessor

class OCRTools:
    def __init__(self, processor="pytesseract"):
        self.processor = processor

    def _process_ocr_output(self, ocr_text: str) -> str:
        return ocr_text.replace(",  ", ".").replace("$", "").replace("RG", "R$")

    def _pytesseract_extract_text_with_ocr(self, image_path: str) -> str:
        return self._process_ocr_output(pytesseract.image_to_string(image_path))

    def _ollama_extract_text_with_ocr(self, image_path: str) -> str:
        ocr = OCRProcessor(model_name="llama3.2-vision:11b")
        return ocr.process_image(
            image_path=image_path,
            format_type="json"
        )

    def extract_text_with_ocr(self, image_path: str) -> str:
        if self.processor == "ollama":
            return self._ollama_extract_text_with_ocr(image_path)
        elif self.processor == "pytesseract":
            return self._pytesseract_extract_text_with_ocr(image_path)