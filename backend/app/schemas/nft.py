from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime


class NFTPuzzleBase(BaseModel):
    puzzle_name: str
    image_url: str
    position_x: int
    position_y: int
    rarity: str
    required_achievements: Optional[Dict[str, Any]] = None


class NFTPuzzleCreate(NFTPuzzleBase):
    pass


class NFTPuzzleResponse(NFTPuzzleBase):
    id: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class UserNFTBase(BaseModel):
    user_wallet: str
    puzzle_id: str
    nft_metadata: Optional[Dict[str, Any]] = None


class UserNFTCreate(UserNFTBase):
    pass


class UserNFTResponse(UserNFTBase):
    id: str
    minted_at: datetime
    solana_signature: Optional[str] = None

    class Config:
        from_attributes = True


class AchievementBase(BaseModel):
    name: str
    description: str
    icon: Optional[str] = None
    required_condition: Dict[str, Any]
    reward_puzzle_id: Optional[str] = None


class AchievementCreate(AchievementBase):
    pass


class AchievementResponse(AchievementBase):
    id: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class UserAchievementBase(BaseModel):
    user_wallet: str
    achievement_id: str
    progress: int = 0


class UserAchievementCreate(UserAchievementBase):
    pass


class UserAchievementResponse(UserAchievementBase):
    id: str
    completed_at: datetime

    class Config:
        from_attributes = True


class PuzzleCollectionResponse(BaseModel):
    """Полная коллекция пазлов пользователя"""
    user_wallet: str
    owned_puzzles: List[UserNFTResponse]
    missing_puzzles: List[NFTPuzzleResponse]
    completion_percentage: float
    can_complete_picture: bool


class AchievementProgressResponse(BaseModel):
    """Прогресс достижений пользователя"""
    user_wallet: str
    achievements: List[dict]  # achievement + progress
    total_achievements: int
    completed_achievements: int
