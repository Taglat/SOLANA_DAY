from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.transaction import Receipt
from app.models.transaction import Transaction
from app.models.business import Business
from app.models.user import User
from app.schemas.transaction import (
    ReceiptCreate, ReceiptResponse, ReceiptScanRequest, ReceiptScanResponse
)
from app.api.api_v1.endpoints.auth import get_current_user
from app.services.qr_service import QRService
from app.services.solana_service import SolanaService
from app.services.nft_service import NFTService
import uuid
import qrcode
import io
import base64
import json
from datetime import datetime, timedelta

router = APIRouter()
qr_service = QRService()
solana_service = SolanaService()
nft_service = NFTService()


@router.post("/generate", response_model=ReceiptResponse)
async def generate_receipt(
    receipt_data: ReceiptCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Генерация чека с QR-кодом для клиента"""
    # Проверяем существование транзакции
    transaction = db.query(Transaction).filter(
        Transaction.id == receipt_data.transaction_id,
        Transaction.business_id == receipt_data.business_id
    ).first()
    
    if not transaction:
        raise HTTPException(
            status_code=404,
            detail="Транзакция не найдена"
        )
    
    # Проверяем права доступа (только владелец бизнеса может генерировать чек)
    business = db.query(Business).filter(
        Business.id == receipt_data.business_id,
        Business.owner_wallet == current_user.wallet_address
    ).first()
    
    if not business:
        raise HTTPException(
            status_code=403,
            detail="Нет прав для генерации чека"
        )
    
    # Создаем данные для QR-кода чека
    qr_data = {
        "receipt_id": str(uuid.uuid4()),
        "transaction_id": receipt_data.transaction_id,
        "business_id": receipt_data.business_id,
        "customer_wallet": receipt_data.customer_wallet,
        "amount_usd": str(receipt_data.amount_usd),
        "timestamp": int(datetime.now().timestamp()),
        "type": "receipt_scan"
    }
    
    # Генерируем QR-код
    qr_code_image = qr_service.generate_qr_code(qr_data)
    
    # Создаем чек в БД
    receipt = Receipt(
        id=qr_data["receipt_id"],
        transaction_id=receipt_data.transaction_id,
        business_id=receipt_data.business_id,
        customer_wallet=receipt_data.customer_wallet,
        amount_usd=receipt_data.amount_usd,
        qr_code_data=json.dumps(qr_data),
        qr_code_image=qr_code_image,
        expires_at=datetime.now() + timedelta(days=7)  # Чек действителен 7 дней
    )
    
    db.add(receipt)
    db.commit()
    db.refresh(receipt)
    
    return receipt


@router.post("/scan", response_model=ReceiptScanResponse)
async def scan_receipt(
    scan_data: ReceiptScanRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Сканирование чека клиентом для получения токенов и NFT"""
    try:
        # Парсим данные QR-кода
        qr_data = json.loads(scan_data.qr_code_data)
        
        # Проверяем тип QR-кода
        if qr_data.get("type") != "receipt_scan":
            raise HTTPException(
                status_code=400,
                detail="Неверный тип QR-кода"
            )
        
        # Находим чек в БД
        receipt = db.query(Receipt).filter(
            Receipt.id == qr_data["receipt_id"],
            Receipt.customer_wallet == current_user.wallet_address
        ).first()
        
        if not receipt:
            raise HTTPException(
                status_code=404,
                detail="Чек не найден"
            )
        
        # Проверяем, не был ли чек уже отсканирован
        if receipt.is_scanned:
            raise HTTPException(
                status_code=400,
                detail="Чек уже был отсканирован"
            )
        
        # Проверяем срок действия чека
        if datetime.now() > receipt.expires_at:
            raise HTTPException(
                status_code=400,
                detail="Срок действия чека истек"
            )
        
        # Получаем информацию о бизнесе
        business = db.query(Business).filter(
            Business.id == receipt.business_id
        ).first()
        
        if not business:
            raise HTTPException(
                status_code=404,
                detail="Бизнес не найден"
            )
        
        # Рассчитываем количество токенов
        tokens_amount = int(float(receipt.amount_usd) * business.tokens_per_dollar)
        
        # Начисляем токены через Solana
        solana_signature = await solana_service.mint_loyalty_tokens(
            current_user.wallet_address,
            tokens_amount,
            receipt.business_id
        )
        
        # Обновляем чек как отсканированный
        receipt.is_scanned = True
        receipt.scanned_at = datetime.now()
        
        # Создаем транзакцию начисления токенов
        transaction = Transaction(
            id=str(uuid.uuid4()),
            customer_wallet=current_user.wallet_address,
            business_id=receipt.business_id,
            transaction_type="EARN",
            amount_usd=receipt.amount_usd,
            tokens_amount=tokens_amount,
            solana_signature=solana_signature
        )
        
        db.add(transaction)
        db.commit()
        
        # Проверяем достижения и начисляем NFT
        nft_earned = None
        try:
            nft_earned = await nft_service.check_achievements_and_mint_nft(
                current_user.wallet_address,
                receipt.business_id,
                tokens_amount,
                db
            )
        except Exception as e:
            # NFT ошибки не должны прерывать процесс начисления токенов
            print(f"NFT error: {e}")
        
        return ReceiptScanResponse(
            success=True,
            message=f"Получено {tokens_amount} токенов!",
            tokens_earned=tokens_amount,
            nft_earned=nft_earned,
            transaction_id=transaction.id
        )
        
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=400,
            detail="Неверный формат QR-кода"
        )
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Ошибка при сканировании чека: {str(e)}"
        )


@router.get("/my", response_model=list[ReceiptResponse])
async def get_my_receipts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Получение чеков текущего пользователя"""
    receipts = db.query(Receipt).filter(
        Receipt.customer_wallet == current_user.wallet_address
    ).order_by(Receipt.created_at.desc()).all()
    
    return receipts


@router.get("/business/{business_id}", response_model=list[ReceiptResponse])
async def get_business_receipts(
    business_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Получение чеков конкретного бизнеса"""
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
    
    receipts = db.query(Receipt).filter(
        Receipt.business_id == business_id
    ).order_by(Receipt.created_at.desc()).all()
    
    return receipts
