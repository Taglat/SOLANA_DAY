from sqlalchemy import Column, String, DateTime, Integer, Numeric, ForeignKey, JSON, func

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
    metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=func.now())


