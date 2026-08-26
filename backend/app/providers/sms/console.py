"""Console SMS provider: logs OTPs instead of sending them.

Phase 0 default so the auth flow can be developed without MSG91/DLT. Replace
via SMS_PROVIDER=msg91 once the MSG91 adapter lands.
"""

import logging

from app.providers.base import SendResult

logger = logging.getLogger("providers.sms.console")


class ConsoleSMSProvider:
    name = "console"

    async def send_otp(self, phone: str, code: str) -> SendResult:
        logger.info("OTP for %s: %s (console provider — do not use in production)", phone, code)
        return SendResult(ok=True, provider_message_id=f"console-{code}")
