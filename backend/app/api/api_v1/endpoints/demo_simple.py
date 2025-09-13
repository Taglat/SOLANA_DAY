from fastapi import APIRouter, HTTPException, status
from typing import Dict, Any
import uuid
import json
from datetime import datetime, timedelta

router = APIRouter()

# In-memory storage for demo
users_db = {}
receipts_db = {}
transactions_db = {}
puzzles_db = {}
user_nfts_db = {}

@router.post("/register")
async def register_user(user_data: Dict[str, Any]):
    """Регистрация пользователя (демо версия)"""
    wallet_address = user_data.get("wallet_address")
    if not wallet_address:
        raise HTTPException(status_code=400, detail="Wallet address required")
    
    if wallet_address in users_db:
        return {"message": "User already exists", "wallet": wallet_address}
    
    users_db[wallet_address] = {
        "wallet_address": wallet_address,
        "created_at": datetime.now(),
        "token_balance": 0
    }
    
    return {"message": "User registered successfully", "wallet": wallet_address}

@router.get("/user-balance/{wallet_address}")
async def get_user_balance(wallet_address: str):
    """Получение баланса пользователя (демо версия)"""
    user = users_db.get(wallet_address)
    if not user:
        # Создаем пользователя если не существует
        users_db[wallet_address] = {
            "wallet_address": wallet_address,
            "created_at": datetime.now(),
            "token_balance": 0
        }
        user = users_db[wallet_address]
    
    return {"balance": user["token_balance"], "wallet": wallet_address}

@router.post("/update-balance")
async def update_balance(data: Dict[str, Any]):
    """Обновление баланса пользователя (демо версия)"""
    wallet_address = data.get("wallet_address")
    amount = data.get("amount", 0)
    
    if wallet_address not in users_db:
        users_db[wallet_address] = {
            "wallet_address": wallet_address,
            "created_at": datetime.now(),
            "token_balance": 0
        }
    
    users_db[wallet_address]["token_balance"] += amount
    
    return {
        "message": "Balance updated",
        "wallet": wallet_address,
        "new_balance": users_db[wallet_address]["token_balance"]
    }

@router.post("/receipts/generate")
async def generate_receipt(receipt_data: Dict[str, Any]):
    """Генерация чека с QR-кодом (демо версия)"""
    
    # Создаем данные для QR-кода чека
    qr_data = {
        "receipt_id": str(uuid.uuid4()),
        "transaction_id": receipt_data.get("transaction_id", str(uuid.uuid4())),
        "business_id": receipt_data.get("business_id", "demo_business"),
        "customer_wallet": receipt_data.get("customer_wallet"),
        "amount_usd": str(receipt_data.get("amount_usd", 0)),
        "timestamp": int(datetime.now().timestamp()),
        "type": "receipt_scan"
    }
    
    # Создаем чек
    receipt = {
        "id": qr_data["receipt_id"],
        "transaction_id": qr_data["transaction_id"],
        "business_id": qr_data["business_id"],
        "customer_wallet": qr_data["customer_wallet"],
        "amount_usd": float(receipt_data.get("amount_usd", 0)),
        "qr_code_data": json.dumps(qr_data),
        "qr_code_image": None,
        "is_scanned": False,
        "scanned_at": None,
        "expires_at": datetime.now() + timedelta(days=7),
        "created_at": datetime.now()
    }
    
    # Сохраняем в памяти
    receipts_db[receipt["id"]] = receipt
    
    return receipt

@router.post("/receipts/scan")
async def scan_receipt(scan_data: Dict[str, Any]):
    """Сканирование чека (демо версия)"""
    try:
        # Парсим данные QR-кода
        qr_data = json.loads(scan_data["qr_code_data"])
        
        # Проверяем тип QR-кода
        if qr_data.get("type") != "receipt_scan":
            raise HTTPException(status_code=400, detail="Неверный тип QR-кода")
        
        # Находим чек
        receipt = receipts_db.get(qr_data["receipt_id"])
        if not receipt:
            raise HTTPException(status_code=404, detail="Чек не найден")
        
        # Проверяем, не был ли чек уже отсканирован
        if receipt["is_scanned"]:
            raise HTTPException(status_code=400, detail="Чек уже был отсканирован")
        
        # Проверяем срок действия чека
        if datetime.now() > receipt["expires_at"]:
            raise HTTPException(status_code=400, detail="Срок действия чека истек")
        
        # Рассчитываем количество токенов (10 токенов за $1)
        tokens_amount = int(receipt["amount_usd"] * 10)
        
        # Обновляем чек как отсканированный
        receipt["is_scanned"] = True
        receipt["scanned_at"] = datetime.now()
        
        # Обновляем баланс пользователя
        wallet_address = qr_data["customer_wallet"]
        if wallet_address not in users_db:
            users_db[wallet_address] = {
                "wallet_address": wallet_address,
                "created_at": datetime.now(),
                "token_balance": 0
            }
        
        users_db[wallet_address]["token_balance"] += tokens_amount
        
        # Создаем транзакцию
        transaction_id = str(uuid.uuid4())
        transactions_db[transaction_id] = {
            "id": transaction_id,
            "customer_wallet": wallet_address,
            "business_id": receipt["business_id"],
            "transaction_type": "EARN",
            "amount_usd": receipt["amount_usd"],
            "tokens_amount": tokens_amount,
            "created_at": datetime.now()
        }
        
        # Проверяем достижения и начисляем NFT (демо)
        nft_earned = None
        if tokens_amount >= 50:  # Если получили много токенов
            nft_earned = f"coffee_bean_{len(transactions_db) % 3 + 1}"
            # Добавляем NFT пользователю
            if wallet_address not in user_nfts_db:
                user_nfts_db[wallet_address] = []
            user_nfts_db[wallet_address].append({
                "id": str(uuid.uuid4()),
                "puzzle_id": nft_earned,
                "minted_at": datetime.now()
            })
        
        return {
            "success": True,
            "message": f"Получено {tokens_amount} токенов!",
            "tokens_earned": tokens_amount,
            "nft_earned": nft_earned,
            "transaction_id": transaction_id
        }
        
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Неверный формат QR-кода")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Ошибка при сканировании чека: {str(e)}")

@router.get("/receipts/my")
async def get_my_receipts():
    """Получение чеков пользователя (демо версия)"""
    return list(receipts_db.values())

@router.post("/coffee-nft/init-coffee-collection")
async def init_coffee_collection():
    """Инициализация NFT коллекции кофейни (демо версия)"""
    try:
        # Создаем пазлы для коллекции
        puzzle_ids = []
        
        # Coffee Beans Collection
        for i in range(1, 4):
            puzzle_id = f"coffee_bean_{i}"
            puzzle = {
                "id": puzzle_id,
                "puzzle_name": f"coffee_bean_{i}",
                "image_url": f"/images/nft_pictures/coffee_beans/coffee_bean_{i}.jpg",
                "position_x": i - 1,
                "position_y": 0,
                "rarity": "common" if i < 3 else "rare"
            }
            puzzles_db[puzzle_id] = puzzle
            puzzle_ids.append(puzzle_id)
        
        # Espresso Collection
        for i in range(1, 4):
            puzzle_id = f"espresso_{i}"
            puzzle = {
                "id": puzzle_id,
                "puzzle_name": f"espresso_{i}",
                "image_url": f"/images/nft_pictures/espresso/espresso_{i}.jpg",
                "position_x": i - 1,
                "position_y": 0,
                "rarity": "common" if i == 1 else "rare" if i == 2 else "epic"
            }
            puzzles_db[puzzle_id] = puzzle
            puzzle_ids.append(puzzle_id)
        
        # Latte Art Collection
        for i in range(1, 4):
            puzzle_id = f"latte_art_{i}"
            puzzle = {
                "id": puzzle_id,
                "puzzle_name": f"latte_art_{i}",
                "image_url": f"/images/nft_pictures/latte_art/latte_art_{i}.jpg",
                "position_x": i - 1,
                "position_y": 0,
                "rarity": "rare" if i == 1 else "epic" if i == 2 else "legendary"
            }
            puzzles_db[puzzle_id] = puzzle
            puzzle_ids.append(puzzle_id)
        
        return {
            "message": "NFT коллекция кофейни успешно инициализирована",
            "puzzles_created": len(puzzle_ids),
            "puzzle_ids": puzzle_ids
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка инициализации коллекции: {str(e)}")

@router.get("/coffee-nft/coffee-collection/{wallet_address}")
async def get_coffee_collection(wallet_address: str):
    """Получение коллекции кофейни для пользователя (демо версия)"""
    try:
        # Получаем все пазлы кофейни
        coffee_puzzles = [p for p in puzzles_db.values() if 'coffee_bean' in p['puzzle_name'] or 'espresso' in p['puzzle_name'] or 'latte_art' in p['puzzle_name']]
        
        # Получаем NFT пользователя
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
        raise HTTPException(status_code=500, detail=f"Ошибка получения коллекции: {str(e)}")
