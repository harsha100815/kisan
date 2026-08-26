"""Null WhatsApp client: no-op stub used until WhatsApp Cloud API adapter lands."""

import logging

from app.providers.base import SendResult

logger = logging.getLogger("providers.whatsapp.null")


class NullWhatsAppClient:
    name = "null"

    async def send_text(self, phone: str, text: str) -> SendResult:
        logger.debug("whatsapp(null) send_text to %s suppressed", phone)
        return SendResult(ok=False, error="whatsapp_provider_disabled")

    async def send_image_document(self, phone: str, image_ref: str, caption: str) -> SendResult:
        logger.debug("whatsapp(null) send_image_document to %s suppressed", phone)
        return SendResult(ok=False, error="whatsapp_provider_disabled")
