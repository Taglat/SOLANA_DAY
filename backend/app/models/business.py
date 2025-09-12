from sqlalchemy import Column, String, DateTime, Boolean, Integer, func

from app.db.base_class import Base


class Business(Base):
    __tablename__ = "businesses"

    id = Column(String, primary_key=True)
    owner_wallet = Column(String, nullable=False)
    name = Column(String, nullable=False)
    category = Column(String, nullable=False)
    description = Column(String, nullable=True)
    tokens_per_dollar = Column(Integer, default=10)
    max_discount_percent = Column(Integer, default=50)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())


