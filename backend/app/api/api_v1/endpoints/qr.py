from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.business import Business
from app.models.user import User
from app.schemas.qr import QRCodeGenerate, QRCodeScan, QRCodeResponse, QRCodeData
from app.api.api_v1.endpoints.auth import get_current_user
from app.services.qr_service import QRService
import qrcode
import io
import base64
from datetime import datetime, timedelta

router = APIRouter()
qr_service = QRService()


@router.post("/generate", response_model=QRCodeResponse)
async def generate_qr_code(
    qr_data: QRCodeGenerate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Генерация QR кода для бизнеса"""
    # Проверяем существование бизнеса
    business = db.query(Business).filter(
        Business.id == qr_data.business_id,
        Business.owner_wallet == current_user.wallet_address
    ).first()
    
    if not business:
        raise HTTPException(
            status_code=404,
            detail="Бизнес не найден"
        )
    
    # Создаем данные для QR кода
    qr_data_obj = QRCodeData(
        user_wallet=current_user.wallet_address,
        amount_usd=qr_data.amount_usd,
        business_id=qr_data.business_id,
        timestamp=int(datetime.now().timestamp()),
        transaction_type=qr_data.transaction_type
    )
    
    # Генерируем QR код
    qr_code_image = qr_service.generate_qr_code(qr_data_obj.dict())
    
    return QRCodeResponse(
        qr_code=qr_code_image,
        qr_data=qr_data_obj,
        expires_at=datetime.now() + timedelta(minutes=15)
    )


@router.post("/scan")
async def scan_qr_code(
    scan_data: QRCodeScan,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Сканирование QR кода"""
    try:
        # Парсим данные QR кода
        qr_data = QRCodeData.parse_raw(scan_data.qr_data)
        
        # Проверяем, что QR код не истек
        if datetime.now().timestamp() - qr_data.timestamp > 900:  # 15 минут
            raise HTTPException(
                status_code=400,
                detail="QR код истек"
            )
        
        # Проверяем существование бизнеса
        business = db.query(Business).filter(
            Business.id == qr_data.business_id,
            Business.is_active == True
        ).first()
        
        if not business:
            raise HTTPException(
                status_code=404,
                detail="Бизнес не найден"
            )
        
        # Проверяем, что сканирует владелец бизнеса
        if business.owner_wallet != scan_data.scanner_wallet:
            raise HTTPException(
                status_code=403,
                detail="Нет прав для сканирования этого QR кода"
            )
        
        return {
            "valid": True,
            "qr_data": qr_data,
            "business": business,
            "message": "QR код успешно отсканирован"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Неверный QR код: {str(e)}"
        )


@router.get("/validate/{qr_data}")
async def validate_qr_code(
    qr_data: str,
    db: Session = Depends(get_db)
):
    """Валидация QR кода без сканирования"""
    try:
        qr_data_obj = QRCodeData.parse_raw(qr_data)
        
        # Проверяем существование бизнеса
        business = db.query(Business).filter(
            Business.id == qr_data_obj.business_id,
            Business.is_active == True
        ).first()
        
        if not business:
            raise HTTPException(
                status_code=404,
                detail="Бизнес не найден"
            )
        
        return {
            "valid": True,
            "business": business,
            "amount_usd": qr_data_obj.amount_usd,
            "transaction_type": qr_data_obj.transaction_type
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Неверный QR код: {str(e)}"
        )
