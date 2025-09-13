from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.nft import NFTPuzzle, UserNFT
from app.models.user import User
from app.api.api_v1.endpoints.auth import get_current_user
import uuid
import json

router = APIRouter()


@router.post("/award-puzzle/{user_wallet}/{puzzle_id}")
async def award_puzzle(
    user_wallet: str, 
    puzzle_id: str, 
    db: Session = Depends(get_db)
):
    """Выдача пазла пользователю"""
    try:
        # Проверяем существование пазла
        puzzle = db.query(NFTPuzzle).filter(NFTPuzzle.id == puzzle_id).first()
        if not puzzle:
            raise HTTPException(status_code=404, detail="Пазл не найден")
        
        # Проверяем, что у пользователя еще нет этого пазла
        existing_nft = db.query(UserNFT).filter(
            UserNFT.user_wallet == user_wallet,
            UserNFT.puzzle_id == puzzle_id
        ).first()
        
        if existing_nft:
            raise HTTPException(status_code=400, detail="У вас уже есть этот пазл")
        
        # Создаем NFT
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
        
        user_nft = UserNFT(
            id=str(uuid.uuid4()),
            user_wallet=user_wallet,
            puzzle_id=puzzle_id,
            nft_metadata=json.dumps(nft_metadata),
            solana_signature=f"nft_{uuid.uuid4().hex[:16]}"
        )
        
        db.add(user_nft)
        db.commit()
        
        return {
            "message": f"Пазл {puzzle.puzzle_name} успешно получен!",
            "nft_id": user_nft.id,
            "puzzle": {
                "id": puzzle.id,
                "name": puzzle.puzzle_name,
                "position": f"{puzzle.position_x},{puzzle.position_y}",
                "rarity": puzzle.rarity,
                "image_url": puzzle.image_url
            }
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка выдачи пазла: {str(e)}")


@router.get("/collection/{user_wallet}")
async def get_user_collection(user_wallet: str, db: Session = Depends(get_db)):
    """Получение коллекции пользователя"""
    # Получаем все пазлы
    all_puzzles = db.query(NFTPuzzle).filter(NFTPuzzle.is_active == True).all()
    
    # Получаем пазлы пользователя
    user_nfts = db.query(UserNFT).filter(UserNFT.user_wallet == user_wallet).all()
    owned_puzzle_ids = {nft.puzzle_id for nft in user_nfts}
    
    # Разделяем на собранные и недостающие
    owned_puzzles = []
    missing_puzzles = []
    
    for puzzle in all_puzzles:
        if puzzle.id in owned_puzzle_ids:
            owned_puzzles.append({
                "id": puzzle.id,
                "name": puzzle.puzzle_name,
                "position_x": puzzle.position_x,
                "position_y": puzzle.position_y,
                "rarity": puzzle.rarity,
                "image_url": puzzle.image_url
            })
        else:
            missing_puzzles.append({
                "id": puzzle.id,
                "name": puzzle.puzzle_name,
                "position_x": puzzle.position_x,
                "position_y": puzzle.position_y,
                "rarity": puzzle.rarity,
                "image_url": puzzle.image_url
            })
    
    # Рассчитываем прогресс
    total_puzzles = len(all_puzzles)
    owned_count = len(owned_puzzles)
    completion_percentage = (owned_count / total_puzzles * 100) if total_puzzles > 0 else 0
    
    # Проверяем, можно ли собрать картинку
    can_complete_picture = len(missing_puzzles) == 0
    
    return {
        "user_wallet": user_wallet,
        "owned_puzzles": owned_puzzles,
        "missing_puzzles": missing_puzzles,
        "completion_percentage": completion_percentage,
        "can_complete_picture": can_complete_picture,
        "total_puzzles": total_puzzles,
        "owned_count": owned_count
    }


@router.get("/complete-picture/{user_wallet}")
async def check_complete_picture(user_wallet: str, db: Session = Depends(get_db)):
    """Проверка завершения картинки"""
    collection = await get_user_collection(user_wallet, db)
    
    if collection["can_complete_picture"]:
        return {
            "complete": True,
            "message": "🎉 Поздравляем! Вы собрали полную картинку ESPRESSO DAY!",
            "prize": "Вы получили эксклюзивный приз - бесплатный кофе в любой кофейне партнера!",
            "completion_percentage": 100.0
        }
    else:
        missing_count = len(collection["missing_puzzles"])
        return {
            "complete": False,
            "message": f"Осталось собрать {missing_count} пазлов",
            "completion_percentage": collection["completion_percentage"]
        }


@router.post("/test-award-all/{user_wallet}")
async def test_award_all_puzzles(user_wallet: str, db: Session = Depends(get_db)):
    """Тестовая функция - выдает все пазлы пользователю"""
    try:
        # Получаем все пазлы
        all_puzzles = db.query(NFTPuzzle).filter(NFTPuzzle.is_active == True).all()
        
        awarded_puzzles = []
        
        for puzzle in all_puzzles:
            # Проверяем, есть ли уже этот пазл
            existing_nft = db.query(UserNFT).filter(
                UserNFT.user_wallet == user_wallet,
                UserNFT.puzzle_id == puzzle.id
            ).first()
            
            if existing_nft:
                continue  # Уже есть
            
            # Создаем NFT
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
            
            user_nft = UserNFT(
                id=str(uuid.uuid4()),
                user_wallet=user_wallet,
                puzzle_id=puzzle.id,
                nft_metadata=json.dumps(nft_metadata),
                solana_signature=f"nft_{uuid.uuid4().hex[:16]}"
            )
            
            db.add(user_nft)
            awarded_puzzles.append(puzzle.puzzle_name)
        
        db.commit()
        
        return {
            "message": f"Выдано {len(awarded_puzzles)} пазлов пользователю {user_wallet}",
            "awarded_puzzles": awarded_puzzles
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка выдачи пазлов: {str(e)}")
