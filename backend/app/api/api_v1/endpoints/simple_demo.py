from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.business import Business
from app.models.user import User
from app.models.transaction import Transaction
import uuid
from decimal import Decimal

router = APIRouter()


@router.post("/seed-basic")
async def seed_basic_demo_data(db: Session = Depends(get_db)):
    """Создание базовых демо-данных без NFT"""
    try:
        # Создаем тестового пользователя
        test_user = User(
            id=str(uuid.uuid4()),
            username="test_user",
            email="test@example.com",
            wallet_address="test_wallet_123",
            token_account="test_token_account_123",
            is_active=True
        )
        
        # Проверяем, есть ли уже пользователь
        existing_user = db.query(User).filter(User.wallet_address == "test_wallet_123").first()
        if not existing_user:
            db.add(test_user)
        
        # Создаем тестовые бизнесы
        businesses_data = [
            {
                "name": "☕ Coffee Shop Central",
                "category": "Cafe",
                "description": "Лучший кофе в городе",
                "tokens_per_dollar": 10,
                "max_discount_percent": 30
            },
            {
                "name": "✂️ Elite Barbershop",
                "category": "Barbershop", 
                "description": "Мужская стрижка и бритье",
                "tokens_per_dollar": 15,
                "max_discount_percent": 50
            },
            {
                "name": "💪 Fitness Club Pro",
                "category": "Fitness",
                "description": "Современный фитнес-клуб",
                "tokens_per_dollar": 5,
                "max_discount_percent": 20
            }
        ]
        
        created_businesses = []
        for business_data in businesses_data:
            # Проверяем, есть ли уже такой бизнес
            existing_business = db.query(Business).filter(
                Business.name == business_data["name"]
            ).first()
            
            if not existing_business:
                business = Business(
                    id=str(uuid.uuid4()),
                    owner_wallet="test_wallet_123",
                    name=business_data["name"],
                    category=business_data["category"],
                    description=business_data["description"],
                    tokens_per_dollar=business_data["tokens_per_dollar"],
                    max_discount_percent=business_data["max_discount_percent"],
                    is_active=True
                )
                db.add(business)
                created_businesses.append(business_data["name"])
        
        db.commit()
        
        return {
            "message": "Базовые демо-данные созданы успешно!",
            "created_businesses": created_businesses,
            "test_user": "test_wallet_123"
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка создания демо-данных: {str(e)}")


@router.get("/businesses")
async def get_demo_businesses(db: Session = Depends(get_db)):
    """Получение всех демо-бизнесов"""
    businesses = db.query(Business).filter(Business.is_active == True).all()
    
    return [
        {
            "id": business.id,
            "name": business.name,
            "category": business.category,
            "description": business.description,
            "tokens_per_dollar": business.tokens_per_dollar,
            "max_discount_percent": business.max_discount_percent
        }
        for business in businesses
    ]


@router.get("/test-purchase/{business_id}/{amount}")
async def test_purchase(
    business_id: str, 
    amount: float, 
    db: Session = Depends(get_db)
):
    """Тестовая покупка для получения токенов"""
    try:
        # Находим бизнес
        business = db.query(Business).filter(Business.id == business_id).first()
        if not business:
            raise HTTPException(status_code=404, detail="Бизнес не найден")
        
        # Рассчитываем токены
        tokens_amount = int(amount * business.tokens_per_dollar)
        
        # Создаем транзакцию
        transaction = Transaction(
            id=str(uuid.uuid4()),
            customer_wallet="test_wallet_123",
            business_id=business_id,
            transaction_type="EARN",
            amount_usd=Decimal(str(amount)),
            tokens_amount=tokens_amount,
            solana_signature=f"test_signature_{uuid.uuid4().hex[:16]}",
            transaction_metadata={"test": True}
        )
        
        db.add(transaction)
        db.commit()
        db.refresh(transaction)
        
        return {
            "message": f"Покупка на ${amount} успешно обработана!",
            "business": business.name,
            "tokens_earned": tokens_amount,
            "transaction_id": transaction.id
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка покупки: {str(e)}")


@router.get("/user-balance/{wallet}")
async def get_user_balance(wallet: str, db: Session = Depends(get_db)):
    """Получение баланса токенов пользователя"""
    # Считаем заработанные токены
    earned_transactions = db.query(Transaction).filter(
        Transaction.customer_wallet == wallet,
        Transaction.transaction_type == "EARN"
    ).all()
    
    # Считаем потраченные токены
    spent_transactions = db.query(Transaction).filter(
        Transaction.customer_wallet == wallet,
        Transaction.transaction_type == "REDEEM"
    ).all()
    
    total_earned = sum(t.tokens_amount for t in earned_transactions)
    total_spent = sum(t.tokens_amount for t in spent_transactions)
    current_balance = total_earned - total_spent
    
    return {
        "wallet": wallet,
        "total_earned": total_earned,
        "total_spent": total_spent,
        "current_balance": current_balance,
        "transactions_count": len(earned_transactions) + len(spent_transactions)
    }
