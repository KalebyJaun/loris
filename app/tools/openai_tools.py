import openai
import json
from typing import Dict, Any

from config import settings
from prompts.purchase_extractor import get_purchase_extractor_prompt, get_purchase_parser, PurchaseInfo
from logger import log

class OpenaiTools:
    def __init__(self):
        self.api_key = settings.open_ai_api_key
        self.model = self.model = settings.ai_model 
        self.client = openai.OpenAI(api_key=self.api_key)
        self.purchase_prompt = get_purchase_extractor_prompt()
        self.purchase_parser = get_purchase_parser()
        log.info("OpenAI tools initialized", model=self.model)

    def get_image_info(self, text: str) -> Dict[str, Any]:
        """
        Extract purchase information from text using OpenAI's API.
        
        Args:
            text (str): The input text to extract purchase information from
        
        Returns:
            Dict[str, Any]: The extracted purchase information
        """
        try:
            # Format the prompt with the input text
            formatted_prompt = self.purchase_prompt.format(text=text)
            log.debug("Sending request to OpenAI", 
                     model=self.model,
                     prompt_length=len(formatted_prompt))

            # Get response from OpenAI
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that extracts purchase information from text."},
                    {"role": "user", "content": formatted_prompt}
                ],
                temperature=0.1  # Lower temperature for more consistent output
            )
            
            # Parse the response using the Pydantic parser
            result = self.purchase_parser.parse(response.choices[0].message.content)
            
            # Convert to dictionary
            return result.model_dump()
            
        except Exception as e:
            log.error(str(e), "Failed to process text with OpenAI")
            # If parsing fails, return a formatted error message
            return {
                "error": "Failed to process text",
                "message": str(e)
            }

        