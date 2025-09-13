from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.nft import NFTPuzzle, UserNFT
import uuid
import json

router = APIRouter()


@router.post("/create-collection")
async def create_picture_collection(db: Session = Depends(get_db)):
    """Создание простой коллекции картинок"""
    try:
        # Создаем 9 картинок для коллекции (3x3 сетка)
        pictures_data = [
            {"name": "coffee_bean_1", "position_x": 0, "position_y": 0, "rarity": "common", "price_tokens": 50},
            {"name": "coffee_bean_2", "position_x": 1, "position_y": 0, "rarity": "common", "price_tokens": 50},
            {"name": "coffee_bean_3", "position_x": 2, "position_y": 0, "rarity": "rare", "price_tokens": 100},
            {"name": "coffee_bean_4", "position_x": 0, "position_y": 1, "rarity": "common", "price_tokens": 50},
            {"name": "coffee_bean_5", "position_x": 1, "position_y": 1, "rarity": "epic", "price_tokens": 200},
            {"name": "coffee_bean_6", "position_x": 2, "position_y": 1, "rarity": "rare", "price_tokens": 100},
            {"name": "coffee_bean_7", "position_x": 0, "position_y": 2, "rarity": "epic", "price_tokens": 200},
            {"name": "coffee_bean_8", "position_x": 1, "position_y": 2, "rarity": "legendary", "price_tokens": 500},
            {"name": "coffee_bean_9", "position_x": 2, "position_y": 2, "rarity": "legendary", "price_tokens": 500}
        ]

        created_pictures = []
        
        for picture_data in pictures_data:
            # Проверяем, есть ли уже такая картинка
            existing_picture = db.query(NFTPuzzle).filter(
                NFTPuzzle.puzzle_name == picture_data["name"]
            ).first()
            
            if existing_picture:
                continue  # Уже есть
            
            picture = NFTPuzzle(
                id=str(uuid.uuid4()),
                puzzle_name=picture_data["name"],
                image_url=f"http://localhost:3000/images/nft_pictures/{picture_data['name']}.svg",
                position_x=picture_data["position_x"],
                position_y=picture_data["position_y"],
                rarity=picture_data["rarity"],
                required_achievements=json.dumps({"price_tokens": picture_data["price_tokens"]}),
                is_active=True
            )
            
            db.add(picture)
            created_pictures.append({
                "id": picture.id,
                "name": picture.puzzle_name,
                "position": f"{picture.position_x},{picture.position_y}",
                "rarity": picture.rarity,
                "price_tokens": picture_data["price_tokens"]
            })
        
        db.commit()
        
        return {
            "message": f"Создано {len(created_pictures)} картинок для коллекции!",
            "pictures": created_pictures,
            "total_pictures": 9
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка создания картинок: {str(e)}")


@router.get("/pictures")
async def get_all_pictures(db: Session = Depends(get_db)):
    """Получение всех доступных картинок"""
    pictures = db.query(NFTPuzzle).filter(NFTPuzzle.is_active == True).all()
    
    result = []
    for picture in pictures:
        try:
            price_tokens = 0
            if picture.required_achievements:
                if isinstance(picture.required_achievements, str):
                    price_tokens = json.loads(picture.required_achievements).get("price_tokens", 0)
                else:
                    price_tokens = picture.required_achievements.get("price_tokens", 0)
        except:
            price_tokens = 0
        
        result.append({
            "id": picture.id,
            "name": picture.puzzle_name,
            "image_url": picture.image_url,
            "position_x": picture.position_x,
            "position_y": picture.position_y,
            "rarity": picture.rarity,
            "price_tokens": price_tokens
        })
    
    return result


@router.post("/buy-picture/{user_wallet}/{picture_id}")
async def buy_picture(
    user_wallet: str,
    picture_id: str,
    db: Session = Depends(get_db)
):
    """Покупка картинки за токены"""
    try:
        # Находим картинку
        picture = db.query(NFTPuzzle).filter(NFTPuzzle.id == picture_id).first()
        if not picture:
            raise HTTPException(status_code=404, detail="Картинка не найдена")
        
        # Проверяем, есть ли уже эта картинка у пользователя
        existing_nft = db.query(UserNFT).filter(
            UserNFT.user_wallet == user_wallet,
            UserNFT.puzzle_id == picture_id
        ).first()
        
        if existing_nft:
            raise HTTPException(status_code=400, detail="У вас уже есть эта картинка")
        
        # Получаем цену в токенах
        price_tokens = 0
        if picture.required_achievements:
            try:
                if isinstance(picture.required_achievements, str):
                    price_tokens = json.loads(picture.required_achievements).get("price_tokens", 0)
                else:
                    price_tokens = picture.required_achievements.get("price_tokens", 0)
            except:
                price_tokens = 0
        
        if price_tokens <= 0:
            raise HTTPException(status_code=400, detail="Картинка недоступна для покупки")
        
        # Создаем NFT
        nft_metadata = {
            "name": f"ESPRESSO DAY Picture - {picture.puzzle_name}",
            "description": f"Картинка #{picture.position_x},{picture.position_y} коллекции ESPRESSO DAY",
            "image": picture.image_url,
            "attributes": [
                {"trait_type": "Rarity", "value": picture.rarity},
                {"trait_type": "Position", "value": f"{picture.position_x},{picture.position_y}"},
                {"trait_type": "Collection", "value": "ESPRESSO DAY"},
                {"trait_type": "Price", "value": f"{price_tokens} tokens"}
            ]
        }
        
        user_nft = UserNFT(
            id=str(uuid.uuid4()),
            user_wallet=user_wallet,
            puzzle_id=picture_id,
            nft_metadata=json.dumps(nft_metadata),
            solana_signature=f"nft_{uuid.uuid4().hex[:16]}"
        )
        
        db.add(user_nft)
        db.commit()
        
        return {
            "message": f"Картинка {picture.puzzle_name} успешно куплена за {price_tokens} токенов!",
            "nft_id": user_nft.id,
            "picture": {
                "id": picture.id,
                "name": picture.puzzle_name,
                "position": f"{picture.position_x},{picture.position_y}",
                "rarity": picture.rarity,
                "price_tokens": price_tokens
            }
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка покупки картинки: {str(e)}")


@router.get("/collection/{user_wallet}")
async def get_user_collection(user_wallet: str, db: Session = Depends(get_db)):
    """Получение коллекции пользователя"""
    # Получаем все картинки
    all_pictures = db.query(NFTPuzzle).filter(NFTPuzzle.is_active == True).all()
    
    # Получаем картинки пользователя
    user_nfts = db.query(UserNFT).filter(UserNFT.user_wallet == user_wallet).all()
    owned_picture_ids = {nft.puzzle_id for nft in user_nfts}
    
    # Разделяем на собранные и недостающие
    owned_pictures = []
    missing_pictures = []
    
    for picture in all_pictures:
        try:
            price_tokens = 0
            if picture.required_achievements:
                if isinstance(picture.required_achievements, str):
                    price_tokens = json.loads(picture.required_achievements).get("price_tokens", 0)
                else:
                    price_tokens = picture.required_achievements.get("price_tokens", 0)
        except:
            price_tokens = 0
        
        picture_data = {
            "id": picture.id,
            "name": picture.puzzle_name,
            "position_x": picture.position_x,
            "position_y": picture.position_y,
            "rarity": picture.rarity,
            "image_url": picture.image_url,
            "price_tokens": price_tokens
        }
        
        if picture.id in owned_picture_ids:
            owned_pictures.append(picture_data)
        else:
            missing_pictures.append(picture_data)
    
    # Рассчитываем прогресс
    total_pictures = len(all_pictures)
    owned_count = len(owned_pictures)
    completion_percentage = (owned_count / total_pictures * 100) if total_pictures > 0 else 0
    
    # Проверяем, можно ли собрать коллекцию
    can_complete_collection = len(missing_pictures) == 0
    
    return {
        "user_wallet": user_wallet,
        "owned_pictures": owned_pictures,
        "missing_pictures": missing_pictures,
        "completion_percentage": completion_percentage,
        "can_complete_collection": can_complete_collection,
        "total_pictures": total_pictures,
        "owned_count": owned_count,
        "missing_count": len(missing_pictures)
    }


@router.get("/collection-status/{user_wallet}")
async def get_collection_status(user_wallet: str, db: Session = Depends(get_db)):
    """Получение статуса коллекции с сообщениями"""
    collection = await get_user_collection(user_wallet, db)
    
    if collection["can_complete_collection"]:
        return {
            "complete": True,
            "message": "🎉 Поздравляем! Вы собрали полную коллекцию ESPRESSO DAY!",
            "prize": "Вы получили эксклюзивный приз - бесплатный кофе в любой кофейне партнера!",
            "completion_percentage": 100.0,
            "owned_count": collection["owned_count"],
            "total_pictures": collection["total_pictures"]
        }
    else:
        missing_count = collection["missing_count"]
        owned_count = collection["owned_count"]
        total_pictures = collection["total_pictures"]
        
        # Разные сообщения в зависимости от прогресса
        if missing_count == 1:
            message = "🔥 Осталось собрать всего 1 картинку! Вы почти у цели!"
        elif missing_count <= 3:
            message = f"💪 Осталось собрать {missing_count} картинки! Продолжайте в том же духе!"
        elif missing_count <= 6:
            message = f"📈 Осталось собрать {missing_count} картинок. Хороший прогресс!"
        else:
            message = f"🚀 Осталось собрать {missing_count} картинок. Начните собирать коллекцию!"
        
        return {
            "complete": False,
            "message": message,
            "completion_percentage": collection["completion_percentage"],
            "owned_count": owned_count,
            "total_pictures": total_pictures,
            "missing_count": missing_count
        }


@router.post("/test-buy-all/{user_wallet}")
async def test_buy_all_pictures(user_wallet: str, db: Session = Depends(get_db)):
    """Тестовая функция - покупает все картинки для пользователя"""
    try:
        # Получаем все картинки
        all_pictures = db.query(NFTPuzzle).filter(NFTPuzzle.is_active == True).all()
        
        bought_pictures = []
        
        for picture in all_pictures:
            # Проверяем, есть ли уже эта картинка
            existing_nft = db.query(UserNFT).filter(
                UserNFT.user_wallet == user_wallet,
                UserNFT.puzzle_id == picture.id
            ).first()
            
            if existing_nft:
                continue  # Уже есть
            
            # Получаем цену
            price_tokens = 0
            if picture.required_achievements:
                try:
                    if isinstance(picture.required_achievements, str):
                        price_tokens = json.loads(picture.required_achievements).get("price_tokens", 0)
                    else:
                        price_tokens = picture.required_achievements.get("price_tokens", 0)
                except:
                    price_tokens = 0
            
            # Создаем NFT
            nft_metadata = {
                "name": f"ESPRESSO DAY Picture - {picture.puzzle_name}",
                "description": f"Картинка #{picture.position_x},{picture.position_y} коллекции ESPRESSO DAY",
                "image": picture.image_url,
                "attributes": [
                    {"trait_type": "Rarity", "value": picture.rarity},
                    {"trait_type": "Position", "value": f"{picture.position_x},{picture.position_y}"},
                    {"trait_type": "Collection", "value": "ESPRESSO DAY"},
                    {"trait_type": "Price", "value": f"{price_tokens} tokens"}
                ]
            }
            
            user_nft = UserNFT(
                id=str(uuid.uuid4()),
                user_wallet=user_wallet,
                puzzle_id=picture.id,
                nft_metadata=json.dumps(nft_metadata),
                solana_signature=f"nft_{uuid.uuid4().hex[:16]}"
            )
            
            db.add(user_nft)
            bought_pictures.append({
                "name": picture.puzzle_name,
                "price_tokens": price_tokens
            })
        
        db.commit()
        
        return {
            "message": f"Куплено {len(bought_pictures)} картинок для пользователя {user_wallet}",
            "bought_pictures": bought_pictures
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка покупки картинок: {str(e)}")
