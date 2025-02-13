import json
import requests
import logging
import re

from functools import wraps
from fastapi.responses import JSONResponse

from model.whatsapp_model import WhatsAppWebhook, Message

class WhatsAppService:
    def __init__(self, token: str, recipient_waid: str, version: str, phone_number_id: str):
        if token == "" or not token:
            raise ValueError("Token not provided but required.")
        if phone_number_id == "" or not phone_number_id:
            raise ValueError("Phone Number ID but required.")
        if version == "" or not version:
            raise ValueError("Version not provided but required.")
        self.headers = {
            "Content-type": "application/json",
            "Authorization": f"Bearer {token}",
        }
        self.recipient_waid = recipient_waid
        self.version = version
        self.phone_number_id = phone_number_id
        self.base_url = f"https://graph.facebook.com/{version}"
        self.url = f"{self.base_url}/{phone_number_id}/messages"

    def _process_text_for_whatsapp(self, text):
        # Remove brackets
        pattern = r"\【.*?\】"
        # Substitute the pattern with an empty string
        text = re.sub(pattern, "", text).strip()

        # Pattern to find double asterisks including the word(s) in between
        pattern = r"\*\*(.*?)\*\*"

        # Replacement pattern with single asterisks
        replacement = r"*\1*"

        # Substitute occurrences of the pattern with the replacement
        whatsapp_style_text = re.sub(pattern, replacement, text)

        return whatsapp_style_text
    
    def _check_webhook_type(self, webhook: WhatsAppWebhook) -> str:
        if webhook.entry[0].changes[0].value.messages:
            return "message"
        elif webhook.entry[0].changes[0].value.statuses:
            return "message_status_update"

    def _generate_response(self, text: str) -> str:
        # Return text in uppercase
        return text.upper()

    def _get_data_to_send(self, recipient, text):
        return json.dumps(
            {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": recipient,
                "type": "text",
                "text": {"preview_url": False, "body": text},
            }
        )
    
    def _send_message(self, data):
        try:
            response =  requests.post(
                url=self.url,
                headers=self.headers,
                data=data
            )
            if response.status_code == 200:
                return response.json()
            response.raise_for_status()
        except Exception as e :
            return response.json()

    def _process_text_message(self, message: Message):
        msg_text = self._generate_response(message.text.body)
        msg_from = message.from_

        data = self._get_data_to_send(msg_from, msg_text)
        self._send_message(data)
    
    def _handle_message(self, message: Message):
        try:
            if message.type == "text":
                self._process_text_message(message)
                return JSONResponse(status_code=200, content={"status": "ok"})
            elif message.type == "image":
                #TODO: handle image messages
                return JSONResponse(status_code=200, content={"status": "ok"})
            elif message.type == "audio":
                #TODO: handle audio messages
                return JSONResponse(status_code=200, content={"status": "ok"})
            else:
                #TODO: handle document messages
                return JSONResponse(status_code=400, content={"status": "error"})

        except json.JSONDecodeError:
            logging.error("Failed to decode JSON")
            return JSONResponse(status_code=400, content={"status": "error", "message": "Invalid JSON provided"})
        
    def handle_webhook(self, webhook: WhatsAppWebhook):
        webhook_type = self._check_webhook_type(webhook=webhook)
        if webhook_type == "message":
            message = webhook.entry[0].changes[0].value.messages[0]
            self._handle_message(message=message)