import logging

from fastapi import APIRouter, Request, Query, HTTPException
from fastapi.responses import PlainTextResponse, JSONResponse
from pydantic import ValidationError

from config import settings
from helpers import fix_keys
from service.whatsapp_service import WhatsAppService
from model.whatsapp_model import WhatsAppWebhook
from logger import log

router = APIRouter()

@router.get("/wpp-webhook")
async def verify(
    mode: str = Query(None, alias="hub.mode"),
    token: str = Query(None, alias="hub.verify_token"),
    challenge: str = Query(None, alias="hub.challenge")
):
    """
    Endpoint for WhatsApp webhook verification (GET).
    Checks verification parameters and responds with challenge if valid.
    """
    try:
        # Check for required parameters
        if not mode or not token:
            log.warning("Missing webhook verification parameters", 
                       mode=bool(mode), 
                       token=bool(token))
            raise HTTPException(status_code=400, detail="Missing parameters")

        # Validate mode and token
        if mode == "subscribe" and token == settings.meta_verify_token:
            log.info("Webhook verification successful")
            return PlainTextResponse(content=challenge, status_code=200)

        log.warning("Webhook verification failed", 
                   mode=mode, 
                   token_provided=bool(token))
        raise HTTPException(status_code=403, detail="Verification failed")
    except HTTPException:
        # Propagate HTTP exceptions
        raise
    except Exception as e:
        log.error(e, "Error during webhook verification")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/wpp-webhook")
async def handle_wpp_message(request: Request):
    """
    Endpoint for handling incoming WhatsApp webhook messages (POST).
    Validates and parses the webhook, then delegates to WhatsAppService.
    """
    try:
        # Parse and fix incoming JSON body
        body = fix_keys(await request.json())
        log.info("Received webhook request", body_type=str(type(body).__name__))
        
        try:
            # Validate and parse webhook model
            webhook = WhatsAppWebhook(**body)
        except ValidationError as e:
            log.error(e, "Invalid webhook format", errors=str(e.errors()))
            raise HTTPException(
                status_code=400,
                detail={"status": "error", "message": f"Invalid Webhook Format: {e.errors()}"}
            )
        
        # Process webhook with WhatsAppService
        wpp = WhatsAppService()
        log.debug("Delegating webhook to WhatsAppService", webhook_type=getattr(webhook, 'type', None))
        response = await wpp.handle_webhook(webhook=webhook)
        log.info("Webhook processed successfully")
        return response

    except HTTPException:
        # Propagate HTTP exceptions
        raise
    except Exception as e:
        log.error(e, "Error processing webhook request")
        raise HTTPException(
            status_code=500,
            detail={"status": "error", "message": "Internal server error"}
        )


