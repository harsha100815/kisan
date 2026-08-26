from fastapi import APIRouter

from app.api.v1 import diagnosis, health, prices

router = APIRouter()
router.include_router(health.router)
router.include_router(diagnosis.router)
router.include_router(prices.router)
