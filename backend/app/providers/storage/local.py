"""Local filesystem object storage (Phase 0 default).

Writes under LOCAL_UPLOAD_DIR and returns a storage reference of the form
"local://<key>". An S3 adapter will return "s3://<bucket>/<key>" later; callers
only ever handle opaque refs.
"""

import logging
from pathlib import Path

from app.core.config import get_settings
from app.providers.base import SendResult  # noqa: F401  (re-export convenience)

logger = logging.getLogger("providers.storage.local")


class LocalObjectStorage:
    name = "local"

    def __init__(self, base_dir: str | None = None) -> None:
        settings = get_settings()
        self._base = Path(base_dir or settings.LOCAL_UPLOAD_DIR)

    async def put(self, key: str, data: bytes, content_type: str) -> str:
        path = self._base / key
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        logger.info("stored %s (%d bytes, %s)", path, len(data), content_type)
        return f"local://{key}"
