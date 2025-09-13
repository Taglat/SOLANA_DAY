from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.transaction import Transaction
from app.models.business import Business
from app.models.user import User
# NFT логика временно отключена
from app.schemas.transaction import (
    PurchaseCreate, RedemptionCreate, TransactionResponse, RedemptionResponse
)
from app.api.api_v1.endpoints.auth import get_current_user
from app.services.solana_service import SolanaService
# NFT сервис временно отключен
import uuid
from decimal import Decimal

router = APIRouter()
solana_service = SolanaService()
# nft_service = NFTService()  # Временно отключен


@router.post("/purchase", response_model=TransactionResponse)
async def create_purchase(
    purchase_data: PurchaseCreate,
    db: Session = Depends(get_db)
):
    """Создание покупки и начисление токенов"""
    # Проверяем существование бизнеса
    business = db.query(Business).filter(
        Business.id == purchase_data.business_id,
        Business.is_active == True
    ).first()
    
    if not business:
        raise HTTPException(
            status_code=404,
            detail="Бизнес не найден"
        )
    
    # Рассчитываем количество токенов
    tokens_amount = int(purchase_data.amount_usd * business.tokens_per_dollar)
    
    # Вызываем Solana smart contract для mint токенов
    solana_signature = await solana_service.mint_loyalty_tokens(
        purchase_data.customer_wallet,
        tokens_amount,
        purchase_data.business_id
    )
    
    # Создаем транзакцию в БД
    transaction = Transaction(
        id=str(uuid.uuid4()),
        customer_wallet=purchase_data.customer_wallet,
        business_id=purchase_data.business_id,
        transaction_type="EARN",
        amount_usd=purchase_data.amount_usd,
        tokens_amount=tokens_amount,
        solana_signature=solana_signature
    )
    
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    
    # Создаем чек для клиента
    from app.models.receipt import Receipt
    from app.services.qr_service import QRService
    import json
    from datetime import datetime, timedelta
    
    qr_service = QRService()
    
    # Создаем данные для QR-кода чека
    qr_data = {
        "receipt_id": str(uuid.uuid4()),
        "transaction_id": transaction.id,
        "business_id": purchase_data.business_id,
        "customer_wallet": purchase_data.customer_wallet,
        "amount_usd": str(purchase_data.amount_usd),
        "timestamp": int(datetime.now().timestamp()),
        "type": "receipt_scan"
    }
    
    # Генерируем QR-код
    qr_code_image = qr_service.generate_qr_code(qr_data)
    
    # Создаем чек
    receipt = Receipt(
        id=qr_data["receipt_id"],
        transaction_id=transaction.id,
        business_id=purchase_data.business_id,
        customer_wallet=purchase_data.customer_wallet,
        amount_usd=purchase_data.amount_usd,
        qr_code_data=json.dumps(qr_data),
        qr_code_image=qr_code_image,
        expires_at=datetime.now() + timedelta(days=7)  # Чек действителен 7 дней
    )
    
    db.add(receipt)
    db.commit()
    
    return transaction


@router.post("/redeem", response_model=RedemptionResponse)
async def redeem_tokens(
    redemption_data: RedemptionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Обмен токенов на скидку"""
    # Проверяем существование бизнеса
    business = db.query(Business).filter(
        Business.id == redemption_data.business_id,
        Business.is_active == True
    ).first()
    
    if not business:
        raise HTTPException(
            status_code=404,
            detail="Бизнес не найден"
        )
    
    # Проверяем максимальную скидку
    if redemption_data.discount_percentage > business.max_discount_percent:
        raise HTTPException(
            status_code=400,
            detail=f"Максимальная скидка: {business.max_discount_percent}%"
        )
    
    # Получаем баланс токенов пользователя
    token_balance = await solana_service.get_token_balance(
        redemption_data.customer_wallet
    )
    
    if token_balance < redemption_data.tokens_amount:
        raise HTTPException(
            status_code=400,
            detail="Недостаточно токенов"
        )
    
    # Вызываем Solana smart contract для burn токенов
    solana_signature = await solana_service.burn_tokens_for_discount(
        redemption_data.customer_wallet,
        redemption_data.tokens_amount
    )
    
    # Рассчитываем сумму скидки (упрощенно)
    discount_amount = Decimal(redemption_data.tokens_amount) / Decimal(100)
    
    # Создаем транзакцию в БД
    transaction = Transaction(
        id=str(uuid.uuid4()),
        customer_wallet=redemption_data.customer_wallet,
        business_id=redemption_data.business_id,
        transaction_type="REDEEM",
        amount_usd=discount_amount,
        tokens_amount=redemption_data.tokens_amount,
        solana_signature=solana_signature
    )
    
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    
    # Генерируем QR код для скидки
    qr_data = {
        "transaction_id": transaction.id,
        "discount_percentage": redemption_data.discount_percentage,
        "discount_amount": str(discount_amount),
        "business_id": redemption_data.business_id,
        "timestamp": int(transaction.created_at.timestamp())
    }
    
    return RedemptionResponse(
        transaction_id=transaction.id,
        qr_code_data=str(qr_data),
        discount_amount=discount_amount,
        remaining_balance=token_balance - redemption_data.tokens_amount
    )


@router.get("/my", response_model=list[TransactionResponse])
async def get_my_transactions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Получение транзакций текущего пользователя"""
    transactions = db.query(Transaction).filter(
        Transaction.customer_wallet == current_user.wallet_address
    ).order_by(Transaction.created_at.desc()).all()
    
    return transactions


@router.get("/business/{business_id}", response_model=list[TransactionResponse])
async def get_business_transactions(
    business_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Получение транзакций конкретного бизнеса"""
    # Проверяем права доступа
    business = db.query(Business).filter(
        Business.id == business_id,
        Business.owner_wallet == current_user.wallet_address
    ).first()
    
    if not business:
        raise HTTPException(
            status_code=404,
            detail="Бизнес не найден"
        )
    
    transactions = db.query(Transaction).filter(
        Transaction.business_id == business_id
    ).order_by(Transaction.created_at.desc()).all()
    
    return transactions
