import requests
import re
import json
from glob import glob
from typing import Dict, Any
import os

from config import settings
from model.whatsapp_model import WhatsAppMedia, WhatsAppWebhook, Message
from logger import log

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
        self.headers = {
            "Content-type": "application/json",
            "Authorization": f"Bearer {self.token}",
        }
        self.base_url = f"https://graph.facebook.com/{self.version}"
        self.url = f"{self.base_url}/{self.phone_number_id}/messages"
        log.info("WhatsAppTools initialized", 
                phone_number_id=self.phone_number_id,
                api_version=self.version)
    
    def _get_media_info(self, image_id: str) -> WhatsAppMedia:
        media_req_url = self.base_url + "/" + image_id
        try:
            response = requests.get(
                url=media_req_url,
                headers=self.headers
            )
            if response.status_code == 200:
                return WhatsAppMedia.model_validate(response.json())
            error_msg = f"Media info request failed: {response.status_code}"
            log.error(error_msg, 
                     status_code=response.status_code,
                     response=response.text)
            response.raise_for_status()
        except Exception as e:
            log.error(str(e), image_id=image_id)
            raise
    
    def _get_media(self, meta_media_info: WhatsAppMedia) -> requests.Response:
        try:
            media_response = requests.get(
                url=meta_media_info.url,
                headers=self.headers,
                stream=True
            )
            media_response.raise_for_status()
            return media_response
        except Exception as e:
            log.error(str(e), media_url=meta_media_info.url)
            raise

    def is_message_already_processed(self, message: Message) -> bool:
        """
        Check if a WhatsApp message (image, audio, document, text) has already been processed and saved locally.
        """
        media_type = message.type
        message_id = message.id
        if not media_type or not message_id:
            log.warning("Message type or ID is missing", 
                        message_id=message_id, 
                        media_type=media_type)
            return False
        
        # Only check supported media types
        if media_type not in ["image", "audio", "text"]:
            log.warning(f"Unsupported media type: {media_type}", message_id=message_id)
            return False

        # Build file path and check existence for each type
        if media_type == "image":
            extension = message.image.mime_type.split('/')[-1] if message.image.mime_type else "jpeg"
            file_path = f"{settings.local_image_path}/{message_id}.{extension}"
            exists = os.path.exists(file_path)
            log.debug("Checking if image already processed", file_path=file_path, exists=exists)
            return exists
        elif media_type == "audio":
            extension = message.audio.mime_type.split('/')[-1].split(';')[0] if message.audio.mime_type else "ogg"
            file_path = f"{settings.localt_audio_path}/{message_id}.{extension}"
            exists = os.path.exists(file_path)
            log.debug("Checking if audio already processed", file_path=file_path, exists=exists)
            return exists
        # elif media_type == "document":
        #     extension = message.document.mime_type.split('/')[-1] if message.document.mime_type else "bin"
        #     file_path = f"{settings.local_document_path}/{message_id}.{extension}"
        #     exists = os.path.exists(file_path)
        #     log.debug("Checking if document already processed", file_path=file_path, exists=exists)
        #     return exists
        elif media_type == "text":
            extension = "txt"
            file_path = f"{settings.local_text_path}/{message_id}.{extension}"
            exists = os.path.exists(file_path)
            log.debug("Checking if text already processed", file_path=file_path, exists=exists)
            return exists

    def process_text_for_whatsapp(self, text: str) -> str:
        """
        Format text for WhatsApp by removing brackets and converting double asterisks to single asterisks.
        """
        # Remove brackets
        pattern = r"\【.*?\】"
        text = re.sub(pattern, "", text).strip()

        # Convert double asterisks to single asterisks
        pattern = r"\*\*(.*?)\*\*"
        replacement = r"*\1*"
        whatsapp_style_text = re.sub(pattern, replacement, text)
        log.debug("Processed text for WhatsApp formatting", original=text, formatted=whatsapp_style_text)
        return whatsapp_style_text
    
    def check_webhook_type(self, webhook: WhatsAppWebhook) -> str:
        """
        Determine the type of incoming WhatsApp webhook event.
        """
        if webhook.entry[0].changes[0].value.messages:
            log.debug("Webhook type: message")
            return "message"
        elif webhook.entry[0].changes[0].value.statuses:
            log.debug("Webhook type: message_status_update")
            return "message_status_update"
        log.debug("Webhook type: unknown")
        return "unknown"

    def get_data_to_send(self, recipient: str, text: str) -> str:
        """
        Prepare message data for WhatsApp API.
        """
        try:
            data = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": recipient,
                "type": "text",
                "text": {"preview_url": False, "body": text},
            }
            log.debug("Prepared message data", 
                     recipient=recipient,
                     message_length=len(text))
            return json.dumps(data)
        except Exception as e:
            log.error(str(e), recipient=recipient)
            raise
    
    def send_message(self, data: str) -> Dict[str, Any]:
        """
        Send a message to the WhatsApp API and handle response.
        """
        try:
            log.info("Sending message to WhatsApp API")
            response = requests.post(
                url=self.url,
                headers=self.headers,
                data=data
            )
            
            if response.status_code == 200:
                log.info("Message sent successfully")
                return response.json()
            
            # Log error details
            error_response = response.json()
            error_msg = f"WhatsApp API error: {response.status_code}"
            log.error(error_msg,
                     status_code=response.status_code,
                     error_details=error_response)
            response.raise_for_status()
            
        except requests.exceptions.RequestException as e:
            log.error(str(e))
            raise
        except Exception as e:
            log.error(str(e))
            raise

    def download_and_save_whatsapp_media_to_local_fs(self, message: Message) -> str:
        """
        Download and save WhatsApp media (image, audio, document, text) to local filesystem.
        Returns the local file path.
        """
        try:
            media_type = message.type
            message_id = message.id
            
            # Handle each media type accordingly
            if media_type == "image":
                media_id = message.image.id
                extension = message.image.mime_type.split('/')[-1] if message.image.mime_type else "jpeg"
                local_media_path = settings.local_image_path
            elif media_type == "audio":
                media_id = message.audio.id
                extension = message.audio.mime_type.split('/')[-1].split(';')[0] if message.audio.mime_type else "ogg"
                local_media_path = settings.localt_audio_path
            elif media_type == "document":
                media_id = message.document.id
                extension = message.document.mime_type.split('/')[-1] if message.document.mime_type else "bin"
                local_media_path = settings.local_document_path
            elif media_type == "text":
                extension = "txt"
                local_media_path = settings.local_text_path
                # Save text message directly
                with open(f"{local_media_path}/{message_id}.{extension}", "w") as file:
                    file.write(message.text.body)
                log.info("Text message saved to local filesystem", 
                         file_path=f"{local_media_path}/{message_id}.{extension}")
                return f"{local_media_path}/{message_id}.{extension}"
            else:
                log.error(f"Unsupported media type: {media_type}", message_id=message.id)
                raise ValueError(f"Unsupported media type: {media_type}")

            log.info("Saving media to local filesystem", media_type=media_type, media_id=media_id)
            meta_media_info = self._get_media_info(media_id)
            media_response = self._get_media(meta_media_info=meta_media_info)

            file_path = f"{local_media_path}/{message_id}.{extension}"
            with open(file_path, "wb") as media_file:
                for chunk in media_response.iter_content(1024):
                    media_file.write(chunk)

            log.info("Media saved successfully", file_path=file_path)
            return file_path

        except Exception as e:
            log.error(str(e), media_id=media_id if 'media_id' in locals() else None)
            raise