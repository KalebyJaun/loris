from glob import glob
import os
from functools import wraps
from fastapi.responses import JSONResponse
from typing import Dict, Any
import json

from model.whatsapp_model import WhatsAppWebhook, Message
from tools.whatsapp_tools import WhatsAppTools
from tools.transformer_tools import OCRTools, LLMTools
from config import settings
from logger import log

class WhatsAppService:
    def __init__(self):
        self.wpp_tools = WhatsAppTools()
        self.ocr_tools = OCRTools()
        self.llm_tools = LLMTools(default_provider="openai")
        log.info("WhatsAppService initialized")

    def _extract_text_from_message(self, message: Message) -> str:
        """
        Save original Message to Local FS and extract text from a Message, handling different types of messages.
        Supported types: text, image, audio.
        """
        try:
            # Save media locally and get local path
            local_media_path = self.wpp_tools.download_and_save_whatsapp_media_to_local_fs(message=message)
            log.debug("Media saved locally", local_media_path=local_media_path, message_type=message.type)

            # Extract text based on message type
            if message.type == "text":
                log.debug("Extracting text from text message", message_id=message.id)
                return message.text.body
            elif message.type == "image":
                log.debug("Extracting text from image message using OCR", message_id=message.id)
                return self.ocr_tools.extract_text_from_image_with_ocr(local_media_path)
            elif message.type == "audio":
                log.debug("Extracting text from audio message using LLMTools", message_id=message.id)
                return self.llm_tools.get_text_from_audio(local_media_path)["text"]
            else:
                log.warning("Unsupported message type for text extraction", message_type=message.type)
                return ""
        except Exception as e:
            log.error(e, "Error extracting text from message", message_id=getattr(message, 'id', None))
            return ""

    def _get_text_info(self, text: str) -> str:
        """
        Extract structured information from text using LLMTools and ensure output is a string.
        """
        try:
            log.debug("Extracting structured info from text", text_length=len(text))
            text_info = self.llm_tools.get_text_info(text)
            # Ensure output is a string
            if isinstance(text_info, dict):
                text_info = json.dumps(text_info)
            elif not isinstance(text_info, str):
                text_info = str(text_info)
            log.debug("Structured info extracted", info_length=len(text_info))
            return text_info
        except Exception as e:
            log.error(e, "Error extracting structured info from text")
            return ""
    
    def _save_output_json(self, result: str, message_id: str) -> None:
        """
        Save the output JSON to a file for later analysis or auditing.
        """
        try:
            output_path = os.path.join(settings.local_json_output_path, f"{message_id}.json")
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(result)
            log.info("Output JSON saved successfully", file_path=output_path)
        except Exception as e:
            log.error(e, "Error saving output JSON", file_path=output_path)

    def _handle_message(self, message: Message) -> JSONResponse:
        """
        Main handler for incoming WhatsApp messages. Checks if already processed, extracts text, gets info, saves output, and sends response.
        """
        try:
            if not message or not message.type:
                log.error("Invalid message format received")
                raise ValueError("Invalid message format")
            
            # Check if message was already processed
            if self.wpp_tools.is_message_already_processed(message):
                log.info("Message already processed", message_id=message.id)
                return JSONResponse(
                    status_code=200,
                    content={"status": "skipped", "message": "Message already processed"}
                )

            log.info("Handling message", message_type=message.type, message_id=message.id)

            # Extract text from message
            msg_text = self._extract_text_from_message(message)
            log.debug("Text extracted from message", message_id=message.id, text_length=len(msg_text))
            
            # Get structured info from text
            text_info = self._get_text_info(msg_text)
            log.debug("Structured info obtained", message_id=message.id, info_length=len(text_info))

            # Save output JSON
            self._save_output_json(text_info, message.id)
            log.info("Message handled successfully", message_id=message.id)

            # Prepare and send WhatsApp response
            data = self.wpp_tools.get_data_to_send(message.from_, text_info)
            self.wpp_tools.send_message(data)
            log.info("Message sent successfully", message_id=message.id)

            return JSONResponse(
                status_code=200,
                content={"status": "success", "message": "Message handled successfully", "data": text_info}
            )

        except Exception as e:
            log.error(e, "Error handling message", message_id=getattr(message, 'id', 'unknown'))
            return JSONResponse(
                status_code=500,
                content={"status": "error", "message": str(e)}
            )

    async def handle_webhook(self, webhook: WhatsAppWebhook) -> JSONResponse:
        """
        Main entrypoint for WhatsApp webhook events. Handles message and status update events.
        """
        try:
            if not webhook or not webhook.entry:
                log.error("Invalid webhook format received")
                raise ValueError("Invalid webhook format")

            webhook_type = self.wpp_tools.check_webhook_type(webhook=webhook)
            log.info("Processing webhook", webhook_type=webhook_type)

            if webhook_type == "message":
                message = webhook.entry[0].changes[0].value.messages[0]
                return self._handle_message(message=message)
            else:
                log.info("Webhook processed (not a message)", webhook_type=webhook_type)
                return JSONResponse(
                    status_code=200,
                    content={"status": "ok", "message": f"Processed {webhook_type} webhook"}
                )
        except Exception as e:
            log.error(e, "Error handling webhook")
            return JSONResponse(
                status_code=500,
                content={"status": "error", "message": str(e)}
            )