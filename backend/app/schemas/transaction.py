from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
from decimal import Decimal


class TransactionBase(BaseModel):
    customer_wallet: str
    business_id: str
    transaction_type: str  # EARN, REDEEM
    amount_usd: Decimal
    tokens_amount: int


class TransactionCreate(TransactionBase):
    solana_signature: Optional[str] = None
    transaction_metadata: Optional[Dict[str, Any]] = None


class TransactionResponse(TransactionBase):
    id: str
    solana_signature: Optional[str] = None
    transaction_metadata: Optional[Dict[str, Any]] = None
    created_at: datetime

    class Config:
        from_attributes = True


class PurchaseCreate(BaseModel):
    business_id: str
    amount_usd: Decimal
    customer_wallet: str


class RedemptionCreate(BaseModel):
    business_id: str
    tokens_amount: int
    discount_percentage: int
    customer_wallet: str


class RedemptionResponse(BaseModel):
    transaction_id: str
    qr_code_data: str
    discount_amount: Decimal
    remaining_balance: int


class ReceiptCreate(BaseModel):
    transaction_id: str
    business_id: str
    customer_wallet: str
    amount_usd: Decimal


class ReceiptResponse(BaseModel):
    id: str
    transaction_id: str
    business_id: str
    customer_wallet: str
    amount_usd: Decimal
    qr_code_data: str
    qr_code_image: Optional[str]
    is_scanned: bool
    scanned_at: Optional[datetime]
    expires_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True


class ReceiptScanRequest(BaseModel):
    qr_code_data: str
    scanner_wallet: str


class ReceiptScanResponse(BaseModel):
    success: bool
    message: str
    tokens_earned: int
    nft_earned: Optional[str]  # ID полученного NFT
    transaction_id: str
