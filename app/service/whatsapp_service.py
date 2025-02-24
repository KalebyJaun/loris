import json
import requests
import logging
import re
from glob import glob

from functools import wraps
from fastapi.responses import JSONResponse

from model.whatsapp_model import WhatsAppWebhook, Message, WhatsAppMedia
from tools.ollama_tools import OllamaTools
from tools.openai_tools import OpenaiTools
from tools.whatsapp_tools import WhatsAppTools
from tools.cv_tools import extract_text_with_ocr

class WhatsAppService:
    def __init__(self):
        self.wpp_tools = WhatsAppTools()
        self.ai_client = OllamaTools()

    def _process_text_message(self, message: Message):
        msg_text = self.wpp_tools.generate_response(message.text.body)
        msg_from = message.from_

        data = self.wpp_tools.get_data_to_send(msg_from, msg_text)
        self.wpp_tools.send_message(data)

    def _process_image_message(self, message: Message):
        image_id = message.image.id
        msg_from = message.from_

        if self.wpp_tools.is_image_already_processed(image_id):
            print(f"Image with Media ID {image_id} already processed.")
            return

        local_image_path = self.wpp_tools.save_media_to_local_fs(message=message)

        try:
            image_text = extract_text_with_ocr(local_image_path)
            image_info = self.ai_client.get_image_info(image_text.replace(",  ", ".").replace("$", "").replace("RG", "R$"))
        except Exception as e:
            print(f"Error processing image: {e}")

        try:
            data = self.wpp_tools.get_data_to_send(msg_from, image_info)#.model_dump_json(indent=4)
        except Exception as e:
            print(f"Error generating data to send: {e}")
        self.wpp_tools.send_message(data)
        
    
    def _handle_message(self, message: Message):
        try:
            if message.type == "text":
                self._process_text_message(message)
                return JSONResponse(status_code=200, content={"status": "ok"})
            elif message.type == "image":
                self._process_image_message(message)
                return JSONResponse(status_code=200, content={"status": "ok"})
            elif message.type == "audio":
                #TODO: handle audio messages
                return JSONResponse(status_code=200, content={"status": "ok"})
            else:
                #TODO: handle document messages
                return JSONResponse(status_code=400, content={"status": "error"})

        except:
            return JSONResponse(status_code=400, content={"status": "error"})
        
    def handle_webhook(self, webhook: WhatsAppWebhook):
        webhook_type = self.wpp_tools.check_webhook_type(webhook=webhook)
        if webhook_type == "message":
            message = webhook.entry[0].changes[0].value.messages[0]
            self._handle_message(message=message)