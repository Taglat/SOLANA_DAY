from sqlalchemy import Column, String, DateTime, Boolean, func

from app.db.base_class import Base


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True)  # Solana public key
    email = Column(String, unique=True, nullable=True)
    username = Column(String, unique=True)
    wallet_address = Column(String, unique=True, nullable=False)
    token_account = Column(String, nullable=True)  # Associated Token Account
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    last_login = Column(DateTime, nullable=True)


