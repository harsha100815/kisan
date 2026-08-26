from fastapi import APIRouter

from app.api.v1 import diagnosis, health

router = APIRouter()
router.include_router(health.router)
router.include_router(diagnosis.router)
