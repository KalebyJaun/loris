from glob import glob
import os
from functools import wraps
from fastapi.responses import JSONResponse
from typing import Optional, Dict, Any
import json

from model.whatsapp_model import WhatsAppWebhook, Message, WhatsAppMedia
from tools.whatsapp_tools import WhatsAppTools
from tools.transformer_tools import OCRTools, LLMTools
from logger import log

class WhatsAppService:
    def __init__(self):
        self.wpp_tools = WhatsAppTools()
        self.ocr_tools = OCRTools()
        self.llm_tools = LLMTools(default_provider="openai")
        log.info("WhatsAppService initialized")

    def __cleanup_local_file(self, file_path: str) -> None:
        """Clean up local files after processing"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                log.info("File cleaned up successfully", file_path=file_path)
        except Exception as e:
            log.error(e, "Error cleaning up file", file_path=file_path)

    def __process_text_message(self, message: Message) -> Dict[str, Any]:
        try:
            log.info("Processing text message", message_id=message.id)
            msg_text = self.wpp_tools.generate_response(message.text.body)
            msg_from = message.from_

            data = self.wpp_tools.get_data_to_send(msg_from, msg_text)
            self.wpp_tools.send_message(data)
            log.info("Text message processed successfully", message_id=message.id)
            return {"status": "success", "message": "Text message processed"}
        except Exception as e:
            log.error(e, "Error processing text message", message_id=message.id)
            raise

    def __process_image_message(self, message: Message) -> Dict[str, Any]:
        image_id = message.image.id
        msg_from = message.from_
        local_image_path = None

        try:
            log.info("Processing image message", image_id=image_id)
            
            if self.wpp_tools.is_image_already_processed(image_id):
                log.info("Image already processed", image_id=image_id)
                return {"status": "skipped", "message": "Image already processed"}

            local_image_path = self.wpp_tools.save_media_to_local_fs(message=message)
            if not local_image_path or not os.path.exists(local_image_path):
                raise FileNotFoundError("Failed to save image locally")

            image_text = self.ocr_tools.extract_text_from_image_with_ocr(local_image_path)
            if not image_text:
                raise ValueError("No text could be extracted from the image")

            # Log OCR output
            # log.info("OCR output", 
            #         image_id=image_id,
            #         ocr_text=image_text)

            # Use LLMTools for extraction with automatic fallback
            text_info = self.llm_tools.get_text_info(image_text)
            log.info("Image processed with LLMTools", image_id=image_id, extracted_info=text_info)

            if not text_info:
                raise ValueError("Failed to extract information from image text")

            # Ensure image_info is a string
            if isinstance(text_info, dict):
                text_info = json.dumps(text_info)
            elif not isinstance(text_info, str):
                text_info = str(text_info)

            data = self.wpp_tools.get_data_to_send(msg_from, text_info)
            self.wpp_tools.send_message(data)
            log.info("Image message processed successfully", image_id=image_id)
            return {"status": "success", "message": "Image processed successfully"}

        except Exception as e:
            log.error(e, "Error processing image", image_id=image_id)
            raise
        finally:
            if local_image_path:
                self.__cleanup_local_file(local_image_path)

    def _handle_message(self, message: Message) -> JSONResponse:
        try:
            if not message or not message.type:
                raise ValueError("Invalid message format")

            log.info("Handling message", message_type=message.type, message_id=message.id)

            if message.type == "text":
                result = self.__process_text_message(message)
                return JSONResponse(status_code=200, content=result)
            elif message.type == "image":
                result = self.__process_image_message(message)
                return JSONResponse(status_code=200, content=result)
            elif message.type == "audio":
                log.info("Audio message received - not implemented", message_id=message.id)
                return JSONResponse(
                    status_code=501,
                    content={"status": "not_implemented", "message": "Audio processing not implemented"}
                )
            else:
                log.warning("Unsupported message type", 
                           message_type=message.type, 
                           message_id=message.id)
                return JSONResponse(
                    status_code=400,
                    content={"status": "error", "message": "Unsupported message type"}
                )

        except Exception as e:
            log.error(e, "Error handling message", 
                     message_id=message.id if message else "unknown")
            return JSONResponse(
                status_code=500,
                content={"status": "error", "message": str(e)}
            )

    async def handle_webhook(self, webhook: WhatsAppWebhook) -> JSONResponse:
        try:
            if not webhook or not webhook.entry:
                raise ValueError("Invalid webhook format")

            webhook_type = self.wpp_tools.check_webhook_type(webhook=webhook)
            log.info("Processing webhook", webhook_type=webhook_type)

            if webhook_type == "message":
                message = webhook.entry[0].changes[0].value.messages[0]
                return self._handle_message(message=message)
            else:
                log.info("Webhook processed", webhook_type=webhook_type)
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