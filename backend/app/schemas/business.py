from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class BusinessBase(BaseModel):
    name: str
    category: str
    description: Optional[str] = None
    tokens_per_dollar: int = 10
    max_discount_percent: int = 50


class BusinessCreate(BusinessBase):
    pass


class BusinessUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    tokens_per_dollar: Optional[int] = None
    max_discount_percent: Optional[int] = None
    is_active: Optional[bool] = None


class BusinessResponse(BusinessBase):
    id: str
    owner_wallet: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class BusinessAnalytics(BaseModel):
    active_customers: int
    tokens_issued: int
    tokens_redeemed: int
    total_transactions: int
    roi_percentage: float
    transactions_chart: list
    customer_segments: dict
