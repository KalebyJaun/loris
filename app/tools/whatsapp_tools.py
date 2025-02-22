from glob import glob

class WhatsAppTools:
    def __init__(self, token: str, version: str, phone_number_id: str):
        if token == "" or not token:
            raise ValueError("Token not provided but required.")
        if phone_number_id == "" or not phone_number_id:
            raise ValueError("Phone Number ID but required.")
        if version == "" or not version:
            raise ValueError("Version not provided but required.")
        self.send_message_headers = {
            "Content-type": "application/json",
            "Authorization": f"Bearer {token}",
        }
        self.get_media_info_headers = {
            "Content-type": "application/json",
            "Authorization": f"Bearer {token}",
        }
        self.version = version
        self.phone_number_id = phone_number_id
        self.base_url = f"https://graph.facebook.com/{version}"
        self.url = f"{self.base_url}/{phone_number_id}/messages"

    def is_image_already_processed(image_id: str) -> bool:
        return f"../data/{image_id}.jpeg" in glob("../data/*")