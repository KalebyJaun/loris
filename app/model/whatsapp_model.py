from pydantic import BaseModel

from pydantic import BaseModel
from typing import List, Optional

class Profile(BaseModel):
    name: str

class Contact(BaseModel):
    profile: Profile
    wa_id: str

class Metadata(BaseModel):
    display_phone_number: str
    phone_number_id: str

class TextMessage(BaseModel):
    body: str

class ImageMessage(BaseModel):
    mime_type: str
    sha256: str
    id: str
    caption: Optional[str] = None

class AudioMessage(BaseModel):
    mime_type: str
    sha256: str
    id: str
    voice: Optional[bool] = None

class DocumentMessage(BaseModel):
    filename: str
    mime_type: str
    sha256: str
    id: str

class Conversation(BaseModel):
    id: str
    origin: dict

class Pricing(BaseModel):
    billable: bool
    pricing_model: str
    category: str

class Status(BaseModel):
    id: str
    status: str
    timestamp: str
    recipient_id: str
    conversation: Optional[Conversation] = None
    pricing: Optional[Pricing] = None

class Message(BaseModel):
    from_: str
    id: str
    timestamp: str
    type: str
    text: Optional[TextMessage] = None
    image: Optional[ImageMessage] = None
    audio: Optional[AudioMessage] = None
    document: Optional[DocumentMessage] = None

class Value(BaseModel):
    messaging_product: str
    metadata: Metadata
    contacts: Optional[List[Contact]] = None
    messages: Optional[List[Message]] = None
    statuses: Optional[List[Status]] = None

class Change(BaseModel):
    value: Value
    field: str

class Entry(BaseModel):
    id: str
    changes: List[Change]

class WhatsAppWebhook(BaseModel):
    object: str
    entry: List[Entry]

class WhatsAppMedia(BaseModel):
    messaging_product:  str
    url: str
    mime_type: str
    sha256: str
    file_size: int
    id: str