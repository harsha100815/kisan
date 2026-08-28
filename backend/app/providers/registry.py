"""Provider factories driven by environment configuration.

The rest of the application must use these getters instead of instantiating
adapters directly. Unknown provider names fail loudly at startup.
"""

from app.core.config import Settings, get_settings
from app.providers.base import (
    MandiPriceSource,
    ObjectStorage,
    SMSProvider,
    VisionProvider,
    WhatsAppClient,
)
from app.providers.mandi.datagov_stub import StubMandiPriceSource
from app.providers.sms.console import ConsoleSMSProvider
from app.providers.storage.local import LocalObjectStorage
from app.providers.vision.null import NullVisionProvider
from app.providers.whatsapp.null import NullWhatsAppClient


def get_vision_provider(settings: Settings | None = None) -> VisionProvider:
    settings = settings or get_settings()
    match settings.VISION_PROVIDER:
        case "null":
            return NullVisionProvider()
        case "openai":
            from app.providers.vision.openai_like import OpenAIVisionProvider

            return OpenAIVisionProvider(settings.OPENAI_API_KEY, settings.OPENAI_VISION_MODEL)
        case _:
            raise ValueError(f"Unknown VISION_PROVIDER: {settings.VISION_PROVIDER}")


def get_sms_provider(settings: Settings | None = None) -> SMSProvider:
    settings = settings or get_settings()
    match settings.SMS_PROVIDER:
        case "console":
            return ConsoleSMSProvider()
        case "msg91":
            raise NotImplementedError("MSG91 adapter lands with the auth phase")
        case _:
            raise ValueError(f"Unknown SMS_PROVIDER: {settings.SMS_PROVIDER}")


def get_whatsapp_client(settings: Settings | None = None) -> WhatsAppClient:
    settings = settings or get_settings()
    match settings.WHATSAPP_PROVIDER:
        case "null":
            return NullWhatsAppClient()
        case "cloud_api":
            raise NotImplementedError("WhatsApp Cloud API adapter lands in a later phase")
        case _:
            raise ValueError(f"Unknown WHATSAPP_PROVIDER: {settings.WHATSAPP_PROVIDER}")


def get_mandi_price_source(settings: Settings | None = None) -> MandiPriceSource:
    settings = settings or get_settings()
    match settings.MANDI_PRICE_SOURCE:
        case "stub":
            return StubMandiPriceSource()
        case "datagov":
            if not settings.DATAGOV_API_KEY:
                raise ValueError("MANDI_PRICE_SOURCE=datagov requires DATAGOV_API_KEY")
            from app.providers.mandi.datagov import DataGovMandiPriceSource

            return DataGovMandiPriceSource(settings.DATAGOV_API_KEY)
        case _:
            raise ValueError(f"Unknown MANDI_PRICE_SOURCE: {settings.MANDI_PRICE_SOURCE}")


def get_storage(settings: Settings | None = None) -> ObjectStorage:
    settings = settings or get_settings()
    match settings.STORAGE_PROVIDER:
        case "local":
            return LocalObjectStorage()
        case "s3":
            raise NotImplementedError("S3 adapter lands with production infra")
        case _:
            raise ValueError(f"Unknown STORAGE_PROVIDER: {settings.STORAGE_PROVIDER}")
