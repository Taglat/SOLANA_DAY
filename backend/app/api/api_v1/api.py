from fastapi import APIRouter
from app.api.api_v1.endpoints import auth, business, transactions, qr, demo, nft, simple_nft, nft_collection, simple_demo, nft_pictures, simple_pictures, qr_nft_integration, receipts, coffee_nft

router = APIRouter()

# Включаем все эндпоинты
router.include_router(auth.router, prefix="/auth", tags=["authentication"])
router.include_router(business.router, prefix="/business", tags=["business"])
router.include_router(transactions.router, prefix="/transactions", tags=["transactions"])
router.include_router(qr.router, prefix="/qr", tags=["qr-codes"])
router.include_router(demo.router, prefix="/demo", tags=["demo"])
router.include_router(nft.router, prefix="/nft", tags=["nft-puzzles"])
router.include_router(simple_nft.router, prefix="/simple-nft", tags=["simple-nft"])
router.include_router(nft_collection.router, prefix="/nft-collection", tags=["nft-collection"])
router.include_router(simple_demo.router, prefix="/simple-demo", tags=["simple-demo"])
router.include_router(nft_pictures.router, prefix="/nft-pictures", tags=["nft-pictures"])
router.include_router(simple_pictures.router, prefix="/simple-pictures", tags=["simple-pictures"])
router.include_router(qr_nft_integration.router, prefix="/qr-nft", tags=["qr-nft-integration"])
router.include_router(receipts.router, prefix="/receipts", tags=["receipts"])
router.include_router(coffee_nft.router, prefix="/coffee-nft", tags=["coffee-nft"])
