from fastapi import APIRouter, HTTPException, status
import uuid

router = APIRouter()

# In-memory storage for demo
puzzles_db = {}
achievements_db = {}
user_nfts_db = {}

@router.post("/init-coffee-collection")
async def init_coffee_collection():
    """Инициализация NFT коллекции кофейни (демо версия)"""
    try:
        # Создаем пазлы для коллекции
        puzzle_ids = []
        
        # Coffee Beans Collection
        for i in range(1, 4):
            puzzle_id = str(uuid.uuid4())
            puzzle = {
                "id": puzzle_id,
                "puzzle_name": f"coffee_bean_{i}",
                "image_url": f"/images/nft_pictures/coffee_beans/coffee_bean_{i}.jpg",
                "position_x": i - 1,
                "position_y": 0,
                "rarity": "common" if i < 3 else "rare",
                "required_achievements": {"min_transactions": i, "business_categories": ["Cafe"]}
            }
            puzzles_db[puzzle_id] = puzzle
            puzzle_ids.append(puzzle_id)
        
        # Espresso Collection
        for i in range(1, 4):
            puzzle_id = str(uuid.uuid4())
            puzzle = {
                "id": puzzle_id,
                "puzzle_name": f"espresso_{i}",
                "image_url": f"/images/nft_pictures/espresso/espresso_{i}.jpg",
                "position_x": i - 1,
                "position_y": 0,
                "rarity": "common" if i == 1 else "rare" if i == 2 else "epic",
                "required_achievements": {"min_spent_usd": 25 * i, "business_categories": ["Cafe"]}
            }
            puzzles_db[puzzle_id] = puzzle
            puzzle_ids.append(puzzle_id)
        
        # Latte Art Collection
        for i in range(1, 4):
            puzzle_id = str(uuid.uuid4())
            puzzle = {
                "id": puzzle_id,
                "puzzle_name": f"latte_art_{i}",
                "image_url": f"/images/nft_pictures/latte_art/latte_art_{i}.jpg",
                "position_x": i - 1,
                "position_y": 0,
                "rarity": "rare" if i == 1 else "epic" if i == 2 else "legendary",
                "required_achievements": {"min_transactions": 5 * i, "min_spent_usd": 75 * i, "business_categories": ["Cafe"]}
            }
            puzzles_db[puzzle_id] = puzzle
            puzzle_ids.append(puzzle_id)
        
        # Создаем достижения
        achievements_data = [
            {
                "id": str(uuid.uuid4()),
                "name": "Первая покупка",
                "description": "Сделайте первую покупку в кофейне",
                "icon": "☕",
                "required_condition": {"type": "transaction_count", "value": 1},
                "reward_puzzle_id": puzzle_ids[0]
            },
            {
                "id": str(uuid.uuid4()),
                "name": "Любитель кофе",
                "description": "Сделайте 3 покупки в кофейне",
                "icon": "☕☕",
                "required_condition": {"type": "transaction_count", "value": 3},
                "reward_puzzle_id": puzzle_ids[2]
            },
            {
                "id": str(uuid.uuid4()),
                "name": "Кофейный гурман",
                "description": "Потратьте $50 в кофейне",
                "icon": "☕☕☕",
                "required_condition": {"type": "spent_amount", "value": 50},
                "reward_puzzle_id": puzzle_ids[4]
            }
        ]
        
        for achievement in achievements_data:
            achievements_db[achievement["id"]] = achievement
        
        return {
            "message": "NFT коллекция кофейни успешно инициализирована",
            "puzzles_created": len(puzzle_ids),
            "achievements_created": len(achievements_data),
            "puzzle_ids": puzzle_ids
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка инициализации коллекции: {str(e)}"
        )

@router.get("/coffee-collection/{wallet_address}")
async def get_coffee_collection(wallet_address: str):
    """Получение коллекции кофейни для пользователя (демо версия)"""
    try:
        # Получаем все пазлы кофейни
        coffee_puzzles = [p for p in puzzles_db.values() if 'coffee_bean' in p['puzzle_name'] or 'espresso' in p['puzzle_name'] or 'latte_art' in p['puzzle_name']]
        
        # Получаем NFT пользователя (демо - возвращаем несколько)
        user_nfts = user_nfts_db.get(wallet_address, [])
        owned_puzzle_ids = [nft['puzzle_id'] for nft in user_nfts]
        
        # Формируем ответ
        owned_puzzles = []
        missing_puzzles = []
        
        for puzzle in coffee_puzzles:
            puzzle_data = {
                "id": puzzle["id"],
                "name": puzzle["puzzle_name"],
                "image_url": puzzle["image_url"],
                "rarity": puzzle["rarity"],
                "position_x": puzzle["position_x"],
                "position_y": puzzle["position_y"]
            }
            
            if puzzle["id"] in owned_puzzle_ids:
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
