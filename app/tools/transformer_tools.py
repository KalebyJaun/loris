import pytesseract
import re, os

from typing import Dict, Any
from logger import log
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_groq import ChatGroq

from config import settings
from prompts.purchase_extractor import get_purchase_extractor_prompt, get_purchase_parser
from logger import log


class OCRTools:
    def __init__(self, processor="pytesseract"):
        self.processor = processor

    def __process_ocr_output(self, ocr_text: str) -> str:
        # Remove non-printable characters, but keep punctuation and currency symbols
        cleaned_text = re.sub(r'[^\x20-\x7E\n]', '', ocr_text)
        # Normalize multiple spaces
        cleaned_text = re.sub(r' +', ' ', cleaned_text)
        # Remove extra blank lines
        cleaned_text = re.sub(r'\n+', '\n', cleaned_text)
        # Strip leading/trailing spaces from each line
        cleaned_text = '\n'.join([line.strip() for line in cleaned_text.splitlines()])
        # Standardize common receipt fields (example)
        cleaned_text = re.sub(r'(?i)valor[: ]+', 'Valor: ', cleaned_text)
        cleaned_text = re.sub(r'(?i)data[: ]+', 'Data: ', cleaned_text)
        cleaned_text = re.sub(r'(?i)hora[: ]+', 'Hora: ', cleaned_text)
        cleaned_text = re.sub(r'(?i)total[: ]+', 'Total: ', cleaned_text)
        # Remove very short lines (noise)
        cleaned_text = '\n'.join([line for line in cleaned_text.splitlines() if len(line) > 2])
        return cleaned_text.strip()
    
    def __save_ocr_text_to_file(self, text: str, image_path: str) -> None:
        
        # Create directory if it doesn't exist
        os.makedirs(settings.local_ocr_text_path, exist_ok=True)
        
        # Generate file name based on image path
        file_name = os.path.basename(image_path).replace('.jpeg', '.txt')
        file_path = os.path.join(settings.local_ocr_text_path, file_name)
        
        # Write text to file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(text)
        
        log.info("OCR text saved to file", file_path=file_path)

    def __pytesseract_extract_text_with_ocr(self, image_path: str) -> str:
        return self.__process_ocr_output(pytesseract.image_to_string(image_path))

    def extract_text_from_image_with_ocr(self, image_path: str) -> str:
        if self.processor == "pytesseract":
            ocr_text = self.__pytesseract_extract_text_with_ocr(image_path)
        else:
            log.error(f"Unsupported OCR processor: {self.processor}")
            raise ValueError(f"Unsupported OCR processor: {self.processor}")
        log.info("OCR text extracted", image_path=image_path, text_length=len(ocr_text))
        self.__save_ocr_text_to_file(ocr_text, image_path)
        return ocr_text

        
class LLMTools:
    def __init__(self, default_provider: str = "openai"):
        self.default_provider = default_provider.lower()
        self.openai_api_key = settings.open_ai_api_key
        self.openai_model = settings.open_ai_model
        self.groq_api_key = settings.groq_api_key
        self.groq_model = settings.groq_model
        self.purchase_prompt = get_purchase_extractor_prompt()
        self.purchase_parser = get_purchase_parser()
        log.info("LLMTools initialized", default_provider=self.default_provider)

    def __get_client(self, provider: str):
        if provider == "openai":
            return ChatOpenAI(api_key=self.openai_api_key, model=self.openai_model, temperature=0.1)
        elif provider == "groq":
            return ChatGroq(api_key=self.groq_api_key, model=self.groq_model, temperature=0.1)
        else:
            raise ValueError(f"Unsupported provider: {provider}")

    def get_text_info(self, text: str) -> Dict[str, Any]:
        """
        Extract purchase information from text using the default LLM provider, with automatic fallback.
        """
        providers = [self.default_provider, "groq" if self.default_provider == "openai" else "openai"]
        last_exception = None
        for provider in providers:
            try:
                client = self.__get_client(provider)
                formatted_prompt = self.purchase_prompt.format(text=text)
                log.debug(f"Sending request to {provider.capitalize()} via LangChain", model=(self.openai_model if provider=="openai" else self.groq_model), prompt_length=len(formatted_prompt))
                messages = [
                    SystemMessage(content="You are a helpful assistant that extracts purchase information from text."),
                    HumanMessage(content=formatted_prompt)
                ]
                response = client.invoke(messages)
                result = self.purchase_parser.parse(response.content)
                log.info(f"Successfully processed image with {provider.capitalize()}", extracted_info=result.model_dump())
                return result.model_dump()
            except Exception as e:
                log.warning(f"{provider.capitalize()} processing failed, trying fallback if available", error=str(e))
                last_exception = e
        log.error(str(last_exception), "Failed to process text with both OpenAI and Groq via LangChain")
        return {
            "error": "Failed to process text with both OpenAI and Groq",
            "message": str(last_exception)
        }