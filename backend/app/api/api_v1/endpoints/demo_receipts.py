from fastapi import APIRouter, HTTPException, status
from app.schemas.transaction import (
    ReceiptCreate, ReceiptResponse, ReceiptScanRequest, ReceiptScanResponse
)
import uuid
import json
from datetime import datetime, timedelta

router = APIRouter()

# In-memory storage for demo
receipts_db = {}
transactions_db = {}

@router.post("/generate", response_model=ReceiptResponse)
async def generate_receipt(receipt_data: ReceiptCreate):
    """Генерация чека с QR-кодом для клиента (демо версия)"""
    
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
    
    # Создаем чек
    receipt = ReceiptResponse(
        id=qr_data["receipt_id"],
        transaction_id=receipt_data.transaction_id,
        business_id=receipt_data.business_id,
        customer_wallet=receipt_data.customer_wallet,
        amount_usd=receipt_data.amount_usd,
        qr_code_data=json.dumps(qr_data),
        qr_code_image=None,
        is_scanned=False,
        scanned_at=None,
        expires_at=datetime.now() + timedelta(days=7),
        created_at=datetime.now()
    )
    
    # Сохраняем в памяти
    receipts_db[receipt.id] = receipt
    
    return receipt

@router.post("/scan", response_model=ReceiptScanResponse)
async def scan_receipt(scan_data: ReceiptScanRequest):
    """Сканирование чека клиентом для получения токенов и NFT (демо версия)"""
    try:
        # Парсим данные QR-кода
        qr_data = json.loads(scan_data.qr_code_data)
        
        # Проверяем тип QR-кода
        if qr_data.get("type") != "receipt_scan":
            raise HTTPException(
                status_code=400,
                detail="Неверный тип QR-кода"
            )
        
        # Находим чек
        receipt = receipts_db.get(qr_data["receipt_id"])
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
        
        # Рассчитываем количество токенов (10 токенов за $1)
        tokens_amount = int(float(receipt.amount_usd) * 10)
        
        # Обновляем чек как отсканированный
        receipt.is_scanned = True
        receipt.scanned_at = datetime.now()
        
        # Создаем транзакцию
        transaction_id = str(uuid.uuid4())
        transactions_db[transaction_id] = {
            "id": transaction_id,
            "customer_wallet": receipt.customer_wallet,
            "business_id": receipt.business_id,
            "transaction_type": "EARN",
            "amount_usd": receipt.amount_usd,
            "tokens_amount": tokens_amount,
            "created_at": datetime.now()
        }
        
        # Проверяем достижения и начисляем NFT (демо)
        nft_earned = None
        if tokens_amount >= 50:  # Если получили много токенов
            nft_earned = f"coffee_bean_{len(transactions_db) % 3 + 1}"
        
        return ReceiptScanResponse(
            success=True,
            message=f"Получено {tokens_amount} токенов!",
            tokens_earned=tokens_amount,
            nft_earned=nft_earned,
            transaction_id=transaction_id
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
async def get_my_receipts():
    """Получение чеков текущего пользователя (демо версия)"""
    # Возвращаем все чеки для демо
    return list(receipts_db.values())

@router.get("/business/{business_id}", response_model=list[ReceiptResponse])
async def get_business_receipts(business_id: str):
    """Получение чеков конкретного бизнеса (демо версия)"""
    return [receipt for receipt in receipts_db.values() if receipt.business_id == business_id]
