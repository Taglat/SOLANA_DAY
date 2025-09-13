from sqlalchemy import Column, String, DateTime, Integer, Numeric, ForeignKey, JSON, func, Boolean

from app.db.base_class import Base


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(String, primary_key=True)
    customer_wallet = Column(String, nullable=False)
    business_id = Column(String, ForeignKey("businesses.id"))
    transaction_type = Column(String, nullable=False)  # EARN, REDEEM
    amount_usd = Column(Numeric(10, 2), nullable=False)
    tokens_amount = Column(Integer, nullable=False)
    solana_signature = Column(String, unique=True)
    transaction_metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=func.now())


class Receipt(Base):
    """Чек с QR-кодом для сканирования клиентом"""
    __tablename__ = "receipts"
    
    id = Column(String, primary_key=True)
    transaction_id = Column(String, ForeignKey("transactions.id"), nullable=False)
    business_id = Column(String, ForeignKey("businesses.id"), nullable=False)
    customer_wallet = Column(String, nullable=False)
    amount_usd = Column(Numeric(10, 2), nullable=False)
    qr_code_data = Column(String, nullable=False)  # Данные для QR-кода
    qr_code_image = Column(String, nullable=True)  # Base64 изображение QR-кода
    is_scanned = Column(Boolean, default=False)  # Был ли чек отсканирован
    scanned_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=False)  # Время истечения чека
    created_at = Column(DateTime, default=func.now())


