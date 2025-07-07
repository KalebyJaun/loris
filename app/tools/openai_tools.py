import json
from typing import Dict, Any

from config import settings
from prompts.purchase_extractor import get_purchase_extractor_prompt, get_purchase_parser, PurchaseInfo
from logger import log
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

class OpenaiTools:
    def __init__(self):
        self.api_key = settings.open_ai_api_key
        self.model = settings.open_ai_model
        self.client = ChatOpenAI(api_key=self.api_key, model=self.model, temperature=0.1)
        self.purchase_prompt = get_purchase_extractor_prompt()
        self.purchase_parser = get_purchase_parser()
        log.info("OpenAI tools initialized", model=self.model)

    def get_image_info(self, text: str) -> Dict[str, Any]:
        """
        Extract purchase information from text using OpenAI's API via LangChain.
        
        Args:
            text (str): The input text to extract purchase information from
        
        Returns:
            Dict[str, Any]: The extracted purchase information
        """
        try:
            # Format the prompt with the input text
            formatted_prompt = self.purchase_prompt.format(text=text)
            log.debug("Sending request to OpenAI via LangChain", 
                     model=self.model,
                     prompt_length=len(formatted_prompt))

            # Use LangChain's chat model
            messages = [
                SystemMessage(content="You are a helpful assistant that extracts purchase information from text."),
                HumanMessage(content=formatted_prompt)
            ]
            response = self.client.invoke(messages)

            # Parse the response using the Pydantic parser
            result = self.purchase_parser.parse(response.content)
            
            # Convert to dictionary
            return result.model_dump()
            
        except Exception as e:
            log.error(str(e), "Failed to process text with OpenAI via LangChain")
            # If parsing fails, return a formatted error message
            return {
                "error": "Failed to process text",
                "message": str(e)
            }

