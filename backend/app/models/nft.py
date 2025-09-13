from sqlalchemy import Column, String, DateTime, Integer, Boolean, ForeignKey, JSON, func
from app.db.base_class import Base


class NFTPuzzle(Base):
    """NFT пазл - отдельный фрагмент картинки"""
    __tablename__ = "nft_puzzles"
    
    id = Column(String, primary_key=True)
    puzzle_name = Column(String, nullable=False)  # "espresso_day_puzzle_1"
    image_url = Column(String, nullable=False)  # URL изображения фрагмента
    position_x = Column(Integer, nullable=False)  # Позиция X в сетке
    position_y = Column(Integer, nullable=False)  # Позиция Y в сетке
    rarity = Column(String, nullable=False)  # "common", "rare", "epic", "legendary"
    required_achievements = Column(JSON, nullable=True)  # Условия получения
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())


class UserNFT(Base):
    """NFT пользователя"""
    __tablename__ = "user_nfts"
    
    id = Column(String, primary_key=True)
    user_wallet = Column(String, nullable=False)  # Убираем внешний ключ для простоты
    puzzle_id = Column(String, ForeignKey("nft_puzzles.id"), nullable=False)
    nft_metadata = Column(JSON, nullable=True)  # Метаданные NFT
    minted_at = Column(DateTime, default=func.now())
    solana_signature = Column(String, unique=True, nullable=True)


class Achievement(Base):
    """Достижение для получения NFT пазлов"""
    __tablename__ = "achievements"
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)  # "first_purchase", "coffee_lover", etc.
    description = Column(String, nullable=False)
    icon = Column(String, nullable=True)  # URL иконки
    required_condition = Column(JSON, nullable=False)  # Условие получения
    reward_puzzle_id = Column(String, ForeignKey("nft_puzzles.id"), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())


class UserAchievement(Base):
    """Достижения пользователя"""
    __tablename__ = "user_achievements"
    
    id = Column(String, primary_key=True)
    user_wallet = Column(String, ForeignKey("users.wallet_address"), nullable=False)
    achievement_id = Column(String, ForeignKey("achievements.id"), nullable=False)
    completed_at = Column(DateTime, default=func.now())
    progress = Column(Integer, default=0)  # Прогресс выполнения (0-100)
