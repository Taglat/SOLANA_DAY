from fastapi import APIRouter
from app.api.api_v1.endpoints.demo_simple import router as demo_router

router = APIRouter()

# Include demo endpoints
router.include_router(demo_router, tags=["demo"])
