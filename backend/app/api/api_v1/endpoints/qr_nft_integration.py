from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.transaction import Transaction
from app.models.business import Business
from app.models.nft import NFTPuzzle, UserNFT
from app.schemas.qr import QRCodeScan
import uuid
import json
from decimal import Decimal

router = APIRouter()


@router.post("/scan-and-earn")
async def scan_qr_and_earn_tokens(
    request: dict,
    db: Session = Depends(get_db)
):
    """Сканирование QR кода и получение токенов + возможность купить NFT картинки"""
    try:
        # Получаем данные из запроса
        qr_data = request.get("qr_data")
        customer_wallet = request.get("customer_wallet")
        
        if not qr_data or not customer_wallet:
            raise HTTPException(status_code=400, detail="Отсутствуют обязательные поля: qr_data, customer_wallet")
        
        # Парсим QR данные
        try:
            qr_info = json.loads(qr_data)
        except:
            raise HTTPException(status_code=400, detail="Неверный формат QR кода")
        
        # Проверяем обязательные поля
        required_fields = ["business_id", "amount_usd", "transaction_type"]
        for field in required_fields:
            if field not in qr_info:
                raise HTTPException(status_code=400, detail=f"Отсутствует поле: {field}")
        
        business_id = qr_info["business_id"]
        amount_usd = float(qr_info["amount_usd"])
        transaction_type = qr_info["transaction_type"]
        
        # Находим бизнес
        business = db.query(Business).filter(
            Business.id == business_id,
            Business.is_active == True
        ).first()
        
        if not business:
            raise HTTPException(status_code=404, detail="Бизнес не найден")
        
        # Рассчитываем токены
        tokens_amount = int(amount_usd * business.tokens_per_dollar)
        
        # Создаем транзакцию
        transaction = Transaction(
            id=str(uuid.uuid4()),
            customer_wallet=customer_wallet,
            business_id=business_id,
            transaction_type=transaction_type,
            amount_usd=Decimal(str(amount_usd)),
            tokens_amount=tokens_amount,
            solana_signature=f"qr_scan_{uuid.uuid4().hex[:16]}",
            transaction_metadata={"qr_scan": True, "qr_data": qr_info}
        )
        
        db.add(transaction)
        db.commit()
        db.refresh(transaction)
        
        # Получаем доступные NFT картинки для покупки
        available_pictures = db.query(NFTPuzzle).filter(
            NFTPuzzle.is_active == True
        ).all()
        
        # Фильтруем картинки, которые пользователь еще не купил
        user_nfts = db.query(UserNFT).filter(UserNFT.user_wallet == customer_wallet).all()
        owned_picture_ids = {nft.puzzle_id for nft in user_nfts}
        
        available_for_purchase = []
        for picture in available_pictures:
            if picture.id not in owned_picture_ids:
                try:
                    price_tokens = 0
                    if picture.required_achievements:
                        if isinstance(picture.required_achievements, str):
                            price_tokens = json.loads(picture.required_achievements).get("price_tokens", 0)
                        else:
                            price_tokens = picture.required_achievements.get("price_tokens", 0)
                except:
                    price_tokens = 0
                
                if price_tokens > 0:  # Только картинки с ценой
                    available_for_purchase.append({
                        "id": picture.id,
                        "name": picture.puzzle_name,
                        "image_url": picture.image_url,
                        "position_x": picture.position_x,
                        "position_y": picture.position_y,
                        "rarity": picture.rarity,
                        "price_tokens": price_tokens
                    })
        
        # Получаем текущий баланс пользователя
        earned_transactions = db.query(Transaction).filter(
            Transaction.customer_wallet == customer_wallet,
            Transaction.transaction_type == "EARN"
        ).all()
        
        spent_transactions = db.query(Transaction).filter(
            Transaction.customer_wallet == customer_wallet,
            Transaction.transaction_type == "REDEEM"
        ).all()
        
        total_earned = sum(t.tokens_amount for t in earned_transactions)
        total_spent = sum(t.tokens_amount for t in spent_transactions)
        current_balance = total_earned - total_spent
        
        return {
            "message": f"QR код успешно отсканирован! Получено {tokens_amount} токенов",
            "transaction": {
                "id": transaction.id,
                "business_name": business.name,
                "amount_usd": amount_usd,
                "tokens_earned": tokens_amount,
                "transaction_type": transaction_type
            },
            "user_balance": {
                "total_earned": total_earned,
                "total_spent": total_spent,
                "current_balance": current_balance
            },
            "available_nft_pictures": available_for_purchase,
            "nft_purchase_message": f"Теперь вы можете купить NFT картинки за токены! У вас {current_balance} токенов."
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка сканирования QR: {str(e)}")


@router.post("/buy-nft-after-qr/{user_wallet}/{picture_id}")
async def buy_nft_after_qr_scan(
    user_wallet: str,
    picture_id: str,
    db: Session = Depends(get_db)
):
    """Покупка NFT картинки после сканирования QR (с проверкой баланса)"""
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
        
        # Проверяем баланс пользователя
        earned_transactions = db.query(Transaction).filter(
            Transaction.customer_wallet == user_wallet,
            Transaction.transaction_type == "EARN"
        ).all()
        
        spent_transactions = db.query(Transaction).filter(
            Transaction.customer_wallet == user_wallet,
            Transaction.transaction_type == "REDEEM"
        ).all()
        
        total_earned = sum(t.tokens_amount for t in earned_transactions)
        total_spent = sum(t.tokens_amount for t in spent_transactions)
        current_balance = total_earned - total_spent
        
        if current_balance < price_tokens:
            raise HTTPException(
                status_code=400, 
                detail=f"Недостаточно токенов. Нужно: {price_tokens}, у вас: {current_balance}"
            )
        
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
        
        # Создаем транзакцию траты токенов
        spend_transaction = Transaction(
            id=str(uuid.uuid4()),
            customer_wallet=user_wallet,
            business_id="nft_purchase",  # Специальный ID для покупки NFT
            transaction_type="REDEEM",
            amount_usd=Decimal("0.00"),
            tokens_amount=price_tokens,
            solana_signature=f"nft_purchase_{uuid.uuid4().hex[:16]}",
            transaction_metadata={"nft_purchase": True, "picture_id": picture_id}
        )
        
        db.add(user_nft)
        db.add(spend_transaction)
        db.commit()
        
        # Получаем обновленный баланс
        new_balance = current_balance - price_tokens
        
        return {
            "message": f"Картинка {picture.puzzle_name} успешно куплена за {price_tokens} токенов!",
            "nft_id": user_nft.id,
            "picture": {
                "id": picture.id,
                "name": picture.puzzle_name,
                "position": f"{picture.position_x},{picture.position_y}",
                "rarity": picture.rarity,
                "price_tokens": price_tokens
            },
            "balance_after_purchase": new_balance,
            "tokens_spent": price_tokens
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка покупки NFT: {str(e)}")


@router.get("/qr-scan-summary/{user_wallet}")
async def get_qr_scan_summary(user_wallet: str, db: Session = Depends(get_db)):
    """Получение сводки по сканированию QR и коллекции"""
    try:
        # Получаем все транзакции пользователя
        all_transactions = db.query(Transaction).filter(
            Transaction.customer_wallet == user_wallet
        ).all()
        
        # Разделяем на заработанные и потраченные
        earned_transactions = [t for t in all_transactions if t.transaction_type == "EARN"]
        spent_transactions = [t for t in all_transactions if t.transaction_type == "REDEEM"]
        
        total_earned = sum(t.tokens_amount for t in earned_transactions)
        total_spent = sum(t.tokens_amount for t in spent_transactions)
        current_balance = total_earned - total_spent
        
        # Получаем коллекцию NFT
        user_nfts = db.query(UserNFT).filter(UserNFT.user_wallet == user_wallet).all()
        owned_picture_ids = {nft.puzzle_id for nft in user_nfts}
        
        all_pictures = db.query(NFTPuzzle).filter(NFTPuzzle.is_active == True).all()
        owned_count = len([p for p in all_pictures if p.id in owned_picture_ids])
        total_pictures = len(all_pictures)
        completion_percentage = (owned_count / total_pictures * 100) if total_pictures > 0 else 0
        
        # Статистика по QR сканированию
        qr_scans = [t for t in earned_transactions if t.transaction_metadata and t.transaction_metadata.get("qr_scan")]
        
        return {
            "user_wallet": user_wallet,
            "token_balance": {
                "total_earned": total_earned,
                "total_spent": total_spent,
                "current_balance": current_balance
            },
            "qr_scan_stats": {
                "total_qr_scans": len(qr_scans),
                "tokens_from_qr": sum(t.tokens_amount for t in qr_scans)
            },
            "nft_collection": {
                "owned_pictures": owned_count,
                "total_pictures": total_pictures,
                "completion_percentage": completion_percentage,
                "can_complete": owned_count == total_pictures
            },
            "recent_transactions": [
                {
                    "id": t.id,
                    "type": t.transaction_type,
                    "amount_usd": float(t.amount_usd),
                    "tokens": t.tokens_amount,
                    "created_at": t.created_at.isoformat(),
                    "is_qr_scan": t.transaction_metadata and t.transaction_metadata.get("qr_scan", False)
                }
                for t in sorted(all_transactions, key=lambda x: x.created_at, reverse=True)[:5]
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка получения сводки: {str(e)}")
