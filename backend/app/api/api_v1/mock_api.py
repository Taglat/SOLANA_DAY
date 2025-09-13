from fastapi import APIRouter
router = APIRouter()
from app.core.config import settings

@router.get("/user-balance/{wallet_address}")
async def get_user_balance(wallet_address: str):
    if hasattr(settings, 'demo_mode') and settings.demo_mode:
        return {"balance": 123}
    return {"balance": 0}

@router.get("/coffee-nft/coffee-collection/{wallet_address}")
async def get_coffee_collection(wallet_address: str):
    if hasattr(settings, 'demo_mode') and settings.demo_mode:
        return {
            "owned_count": 0,
            "total_puzzles": 9,
            "completion_percentage": 0.0,
            "owned_puzzles": []
        }
    return {
        "owned_count": 0,
        "total_puzzles": 0,
        "completion_percentage": 0.0,
        "owned_puzzles": []
    }
