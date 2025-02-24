import requests
import re
import json

from glob import glob

from config import settings
from model.whatsapp_model import WhatsAppMedia, WhatsAppWebhook

class WhatsAppTools:
    def __init__(self):
        self.token = settings.meta_acces_token
        self.phone_number_id = settings.meta_phone_number_id
        self.version = settings.meta_api_version
        if self.token == "" or not self.token:
            raise ValueError("Token not provided but required.")
        if self.phone_number_id == "" or not self.phone_number_id:
            raise ValueError("Phone Number ID but required.")
        if self.version == "" or not self.version:
            raise ValueError("Version not provided but required.")
        self.send_message_headers = {
            "Content-type": "application/json",
            "Authorization": f"Bearer {self.token}",
        }
        self.get_media_info_headers = {
            "Content-type": "application/json",
            "Authorization": f"Bearer {self.token}",
        }
        self.base_url = f"https://graph.facebook.com/{self.version}"
        self.url = f"{self.base_url}/{self.phone_number_id}/messages"

    def is_image_already_processed(image_id: str) -> bool:
        return f"../data/{image_id}.jpeg" in glob("../data/*")
    
    def process_text_for_whatsapp(self, text):
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
    
    def check_webhook_type(self, webhook: WhatsAppWebhook) -> str:
        if webhook.entry[0].changes[0].value.messages:
            return "message"
        elif webhook.entry[0].changes[0].value.statuses:
            return "message_status_update"

    def generate_response(self, text: str) -> str:
        # Return text in uppercase
        return text.upper()

    def get_data_to_send(self, recipient, text):
        return json.dumps(
            {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": recipient,
                "type": "text",
                "text": {"preview_url": False, "body": text},
            }
        )
    
    def send_message(self, data):
        try:
            response =  requests.post(
                url=self.url,
                headers=self.send_message_headers,
                data=data
            )
            if response.status_code == 200:
                return response.json()
            response.raise_for_status()
        except Exception as e :
            print(f"Error sending Message: {e}")
            return response.json()
    
    def get_media_info(self, image_id: str) -> WhatsAppMedia:
        media_req_url = self.base_url + "/" + image_id
        try:
            response = requests.get(
                url=media_req_url,
                headers=self.get_media_info_headers
            )
            if response.status_code == 200:
                print(f"Success getting media info: {response.json()}")
                return WhatsAppMedia.model_validate(response.json())
            response.raise_for_status()
        except Exception as e:
            print(f"Error getting media info: {e}")
            return response.json()