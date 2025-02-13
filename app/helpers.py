from typing import Optional

from model.whatsapp_model import WhatsAppWebhook

def get_message_type(webhook: WhatsAppWebhook) -> Optional[str]:
    for entry in webhook.entry:
        for change in entry.changes:
            if change.value.messages:
                return change.value.messages[0].type
    return None 

def fix_keys(data):
    if isinstance(data, dict):
        return {("from_" if k == "from" else k): fix_keys(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [fix_keys(i) for i in data]
    return data