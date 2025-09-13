from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.nft_service import NFTService
from app.models.nft import Achievement
import uuid

router = APIRouter()
nft_service = NFTService()


@router.post("/init-coffee-collection")
async def init_coffee_collection(db: Session = Depends(get_db)):
    """Инициализация NFT коллекции кофейни"""
    try:
        # Создаем пазлы для коллекции кофейни
        puzzle_ids = nft_service.create_coffee_collection_puzzles(db)
        
        # Создаем достижения для получения NFT
        achievements_data = [
            {
                "name": "Первая покупка",
                "description": "Сделайте первую покупку в кофейне",
                "icon": "☕",
                "required_condition": {
                    "type": "transaction_count",
                    "value": 1
                },
                "reward_puzzle_id": puzzle_ids[0] if len(puzzle_ids) > 0 else None
            },
            {
                "name": "Любитель кофе",
                "description": "Сделайте 3 покупки в кофейне",
                "icon": "☕☕",
                "required_condition": {
                    "type": "transaction_count", 
                    "value": 3
                },
                "reward_puzzle_id": puzzle_ids[1] if len(puzzle_ids) > 1 else None
            },
            {
                "name": "Кофейный гурман",
                "description": "Потратьте $50 в кофейне",
                "icon": "☕☕☕",
                "required_condition": {
                    "type": "spent_amount",
                    "value": 50
                },
                "reward_puzzle_id": puzzle_ids[2] if len(puzzle_ids) > 2 else None
            },
            {
                "name": "Эспрессо мастер",
                "description": "Потратьте $100 в кофейне",
                "icon": "☕☕☕☕",
                "required_condition": {
                    "type": "spent_amount",
                    "value": 100
                },
                "reward_puzzle_id": puzzle_ids[3] if len(puzzle_ids) > 3 else None
            },
            {
                "name": "Латте артист",
                "description": "Потратьте $150 в кофейне",
                "icon": "🎨",
                "required_condition": {
                    "type": "spent_amount",
                    "value": 150
                },
                "reward_puzzle_id": puzzle_ids[4] if len(puzzle_ids) > 4 else None
            },
            {
                "name": "Кофейный коллекционер",
                "description": "Потратьте $250 в кофейне",
                "icon": "👑",
                "required_condition": {
                    "type": "spent_amount",
                    "value": 250
                },
                "reward_puzzle_id": puzzle_ids[5] if len(puzzle_ids) > 5 else None
            }
        ]
        
        created_achievements = []
        for achievement_data in achievements_data:
            achievement = Achievement(
                id=str(uuid.uuid4()),
                name=achievement_data["name"],
                description=achievement_data["description"],
                icon=achievement_data["icon"],
                required_condition=achievement_data["required_condition"],
                reward_puzzle_id=achievement_data["reward_puzzle_id"]
            )
            
            db.add(achievement)
            created_achievements.append(achievement)
        
        db.commit()
        
        return {
            "message": "NFT коллекция кофейни успешно инициализирована",
            "puzzles_created": len(puzzle_ids),
            "achievements_created": len(created_achievements),
            "puzzle_ids": puzzle_ids
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка инициализации коллекции: {str(e)}"
        )


@router.get("/coffee-collection/{wallet_address}")
async def get_coffee_collection(
    wallet_address: str,
    db: Session = Depends(get_db)
):
    """Получение коллекции кофейни для пользователя"""
    try:
        # Получаем все пазлы кофейни
        from app.models.nft import NFTPuzzle, UserNFT
        
        coffee_puzzles = db.query(NFTPuzzle).filter(
            NFTPuzzle.puzzle_name.like('coffee_%') |
            NFTPuzzle.puzzle_name.like('espresso_%') |
            NFTPuzzle.puzzle_name.like('latte_%')
        ).all()
        
        # Получаем NFT пользователя
        user_nfts = db.query(UserNFT).filter(
            UserNFT.user_wallet == wallet_address
        ).all()
        
        owned_puzzle_ids = [nft.puzzle_id for nft in user_nfts]
        
        # Формируем ответ
        owned_puzzles = []
        missing_puzzles = []
        
        for puzzle in coffee_puzzles:
            puzzle_data = {
                "id": puzzle.id,
                "name": puzzle.puzzle_name,
                "image_url": puzzle.image_url,
                "rarity": puzzle.rarity,
                "position_x": puzzle.position_x,
                "position_y": puzzle.position_y
            }
            
            if puzzle.id in owned_puzzle_ids:
                owned_puzzles.append(puzzle_data)
            else:
                missing_puzzles.append(puzzle_data)
        
        completion_percentage = (len(owned_puzzles) / len(coffee_puzzles)) * 100 if coffee_puzzles else 0
        
        return {
            "owned_puzzles": owned_puzzles,
            "missing_puzzles": missing_puzzles,
            "total_puzzles": len(coffee_puzzles),
            "owned_count": len(owned_puzzles),
            "missing_count": len(missing_puzzles),
            "completion_percentage": completion_percentage,
            "can_complete_collection": len(missing_puzzles) == 0
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка получения коллекции: {str(e)}"
        )
