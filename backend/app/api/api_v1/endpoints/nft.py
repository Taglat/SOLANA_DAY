from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.nft import NFTPuzzle, UserNFT, Achievement, UserAchievement
from app.models.user import User
from app.schemas.nft import (
    NFTPuzzleResponse, UserNFTResponse, AchievementResponse,
    PuzzleCollectionResponse, AchievementProgressResponse
)
from app.api.api_v1.endpoints.auth import get_current_user
from app.services.nft_service import NFTService
import uuid

router = APIRouter()
nft_service = NFTService()


@router.get("/puzzles", response_model=list[NFTPuzzleResponse])
async def get_all_puzzles(
    db: Session = Depends(get_db)
):
    """Получение всех доступных пазлов"""
    puzzles = db.query(NFTPuzzle).filter(NFTPuzzle.is_active == True).all()
    return puzzles


@router.get("/collection/{user_wallet}", response_model=PuzzleCollectionResponse)
async def get_user_collection(
    user_wallet: str,
    db: Session = Depends(get_db)
):
    """Получение коллекции пазлов пользователя"""
    # Получаем все пазлы пользователя
    owned_puzzles = db.query(UserNFT).filter(
        UserNFT.user_wallet == user_wallet
    ).all()
    
    # Получаем все доступные пазлы
    all_puzzles = db.query(NFTPuzzle).filter(NFTPuzzle.is_active == True).all()
    
    # Находим недостающие пазлы
    owned_puzzle_ids = {puzzle.puzzle_id for puzzle in owned_puzzles}
    missing_puzzles = [puzzle for puzzle in all_puzzles if puzzle.id not in owned_puzzle_ids]
    
    # Рассчитываем процент завершения
    total_puzzles = len(all_puzzles)
    owned_count = len(owned_puzzles)
    completion_percentage = (owned_count / total_puzzles * 100) if total_puzzles > 0 else 0
    
    # Проверяем, можно ли собрать картинку (все пазлы есть)
    can_complete_picture = len(missing_puzzles) == 0
    
    return PuzzleCollectionResponse(
        user_wallet=user_wallet,
        owned_puzzles=owned_puzzles,
        missing_puzzles=missing_puzzles,
        completion_percentage=completion_percentage,
        can_complete_picture=can_complete_picture
    )


@router.post("/mint/{puzzle_id}", response_model=UserNFTResponse)
async def mint_puzzle_nft(
    puzzle_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Чеканка NFT пазла для пользователя"""
    # Проверяем существование пазла
    puzzle = db.query(NFTPuzzle).filter(
        NFTPuzzle.id == puzzle_id,
        NFTPuzzle.is_active == True
    ).first()
    
    if not puzzle:
        raise HTTPException(
            status_code=404,
            detail="Пазл не найден"
        )
    
    # Проверяем, что у пользователя еще нет этого пазла
    existing_nft = db.query(UserNFT).filter(
        UserNFT.user_wallet == current_user.wallet_address,
        UserNFT.puzzle_id == puzzle_id
    ).first()
    
    if existing_nft:
        raise HTTPException(
            status_code=400,
            detail="У вас уже есть этот пазл"
        )
    
    # Проверяем условия получения (достижения)
    if puzzle.required_achievements:
        can_mint = await nft_service.check_achievement_requirements(
            current_user.wallet_address,
            puzzle.required_achievements,
            db
        )
        
        if not can_mint:
            raise HTTPException(
                status_code=400,
                detail="Не выполнены условия для получения этого пазла"
            )
    
    # Чеканим NFT (заглушка для MVP)
    nft_metadata = {
        "name": f"ESPRESSO DAY Puzzle - {puzzle.puzzle_name}",
        "description": f"Фрагмент #{puzzle.position_x},{puzzle.position_y} коллекции ESPRESSO DAY",
        "image": puzzle.image_url,
        "attributes": [
            {"trait_type": "Rarity", "value": puzzle.rarity},
            {"trait_type": "Position", "value": f"{puzzle.position_x},{puzzle.position_y}"},
            {"trait_type": "Collection", "value": "ESPRESSO DAY"}
        ]
    }
    
    solana_signature = await nft_service.mint_nft(
        current_user.wallet_address,
        nft_metadata
    )
    
    # Создаем запись в БД
    user_nft = UserNFT(
        id=str(uuid.uuid4()),
        user_wallet=current_user.wallet_address,
        puzzle_id=puzzle_id,
        nft_metadata=nft_metadata,
        solana_signature=solana_signature
    )
    
    db.add(user_nft)
    db.commit()
    db.refresh(user_nft)
    
    return user_nft


@router.get("/achievements", response_model=list[AchievementResponse])
async def get_all_achievements(
    db: Session = Depends(get_db)
):
    """Получение всех достижений"""
    achievements = db.query(Achievement).filter(Achievement.is_active == True).all()
    return achievements


@router.get("/achievements/{user_wallet}", response_model=AchievementProgressResponse)
async def get_user_achievements(
    user_wallet: str,
    db: Session = Depends(get_db)
):
    """Получение достижений пользователя с прогрессом"""
    # Получаем все достижения
    all_achievements = db.query(Achievement).filter(Achievement.is_active == True).all()
    
    # Получаем прогресс пользователя
    user_achievements = db.query(UserAchievement).filter(
        UserAchievement.user_wallet == user_wallet
    ).all()
    
    # Создаем словарь прогресса
    progress_dict = {ua.achievement_id: ua.progress for ua in user_achievements}
    
    # Формируем ответ
    achievements_with_progress = []
    completed_count = 0
    
    for achievement in all_achievements:
        progress = progress_dict.get(achievement.id, 0)
        is_completed = progress >= 100
        
        if is_completed:
            completed_count += 1
        
        achievements_with_progress.append({
            "achievement": AchievementResponse.from_orm(achievement),
            "progress": progress,
            "is_completed": is_completed
        })
    
    return AchievementProgressResponse(
        user_wallet=user_wallet,
        achievements=achievements_with_progress,
        total_achievements=len(all_achievements),
        completed_achievements=completed_count
    )


@router.post("/check-achievements/{user_wallet}")
async def check_user_achievements(
    user_wallet: str,
    db: Session = Depends(get_db)
):
    """Проверка и обновление достижений пользователя"""
    updated_achievements = await nft_service.check_and_update_achievements(
        user_wallet, db
    )
    
    return {
        "message": "Достижения проверены",
        "updated_achievements": updated_achievements
    }


@router.get("/picture/{user_wallet}")
async def get_completed_picture(
    user_wallet: str,
    db: Session = Depends(get_db)
):
    """Получение собранной картинки (если все пазлы есть)"""
    collection = await get_user_collection(user_wallet, db)
    
    if not collection.can_complete_picture:
        raise HTTPException(
            status_code=400,
            detail="Не все пазлы собраны для завершения картинки"
        )
    
    # Возвращаем URL полной картинки
    return {
        "picture_url": "https://example.com/espresso-day-complete.jpg",
        "message": "Поздравляем! Вы собрали полную картинку ESPRESSO DAY!",
        "completion_percentage": 100.0
    }
