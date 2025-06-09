from glob import glob
import os
from functools import wraps
from fastapi.responses import JSONResponse
from typing import Optional, Dict, Any
import json

from model.whatsapp_model import WhatsAppWebhook, Message, WhatsAppMedia
from tools.ollama_tools import OllamaTools
from tools.openai_tools import OpenaiTools
from tools.whatsapp_tools import WhatsAppTools
from tools.cv_tools import OCRTools
from logger import log

class WhatsAppService:
    def __init__(self):
        self.wpp_tools = WhatsAppTools()
        self.ai_client = OllamaTools()
        self.ocr_tools = OCRTools()
        self.openai_tools = OpenaiTools()
        log.info("WhatsAppService initialized")

    def _cleanup_local_file(self, file_path: str) -> None:
        """Clean up local files after processing"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                log.info("File cleaned up successfully", file_path=file_path)
        except Exception as e:
            log.error(e, "Error cleaning up file", file_path=file_path)

    def _process_text_message(self, message: Message) -> Dict[str, Any]:
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

    def _process_image_message(self, message: Message) -> Dict[str, Any]:
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

            image_text = self.ocr_tools.extract_text_with_ocr(local_image_path)
            if not image_text:
                raise ValueError("No text could be extracted from the image")

            # Log OCR output
            log.info("OCR output", 
                    image_id=image_id,
                    ocr_text=image_text)

            # Try OpenAI first, fallback to Ollama if needed
            try:
                image_info = self.openai_tools.get_image_info(image_text)
                log.info("Successfully processed image with OpenAI", 
                        image_id=image_id,
                        extracted_info=image_info)
            except Exception as e:
                log.warning("OpenAI processing failed, falling back to Ollama", 
                           image_id=image_id, 
                           error=str(e))
                image_info = self.ai_client.get_image_info(image_text)
                log.info("Successfully processed image with Ollama", 
                        image_id=image_id,
                        extracted_info=image_info)

            if not image_info:
                raise ValueError("Failed to extract information from image text")

            # Ensure image_info is a string
            if isinstance(image_info, dict):
                image_info = json.dumps(image_info)
            elif not isinstance(image_info, str):
                image_info = str(image_info)

            data = self.wpp_tools.get_data_to_send(msg_from, image_info)
            self.wpp_tools.send_message(data)
            log.info("Image message processed successfully", image_id=image_id)
            return {"status": "success", "message": "Image processed successfully"}

        except Exception as e:
            log.error(e, "Error processing image", image_id=image_id)
            raise
        finally:
            if local_image_path:
                self._cleanup_local_file(local_image_path)

    def _handle_message(self, message: Message) -> JSONResponse:
        try:
            if not message or not message.type:
                raise ValueError("Invalid message format")

            log.info("Handling message", message_type=message.type, message_id=message.id)

            if message.type == "text":
                result = self._process_text_message(message)
                return JSONResponse(status_code=200, content=result)
            elif message.type == "image":
                result = self._process_image_message(message)
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