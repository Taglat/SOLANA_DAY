from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class QRCodeData(BaseModel):
    user_wallet: str
    amount_usd: float
    business_id: str
    timestamp: int
    transaction_type: str  # PURCHASE, REDEMPTION


class QRCodeGenerate(BaseModel):
    business_id: str
    amount_usd: float
    transaction_type: str


class QRCodeScan(BaseModel):
    qr_data: str
    scanner_wallet: str  # Business wallet scanning the QR


class QRCodeResponse(BaseModel):
    qr_code: str  # Base64 encoded QR code image
    qr_data: QRCodeData
    expires_at: datetime
