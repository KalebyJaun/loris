import logging

from fastapi import APIRouter, Request, Query, HTTPException
from fastapi.responses import PlainTextResponse
from pydantic import ValidationError

from config import settings
from helpers import fix_keys
from service.whatsapp_service import WhatsAppService
from model.whatsapp_model import WhatsAppWebhook

router = APIRouter()

@router.get("/wpp-webhook")
async def verify(
    mode: str = Query(None, alias="hub.mode"),
    token: str = Query(None, alias="hub.verify_token"),
    challenge: str = Query(None, alias="hub.challenge")
):
    if not mode or not token:
        logging.info("MISSING_PARAMETER")
        raise HTTPException(status_code=400, detail="Missing parameters")

    if mode == "subscribe" and token == settings.meta_verify_token:
        logging.info("WEBHOOK_VERIFIED")
        return PlainTextResponse(content=challenge, status_code=200)

    logging.info("VERIFICATION_FAILED")
    raise HTTPException(status_code=403, detail="Verification failed")

@router.post("/wpp-webhook")
async def handle_wpp_message(request: Request):
    body = fix_keys(await request.json())
    print(body)
    
    try:
        webhook = WhatsAppWebhook(**body)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=f"Invalid Webhook Format: {e.errors()}")
    
    wpp = WhatsAppService(
        token=settings.meta_acces_token,
        recipient_waid=settings.meta_recipient_wand,
        phone_number_id=settings.meta_phone_number_id,
        version=settings.meta_api_version
    )
    return wpp.handle_webhook(webhook=webhook)
    

