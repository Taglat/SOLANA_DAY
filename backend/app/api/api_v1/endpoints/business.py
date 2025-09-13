from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.business import Business
from app.models.user import User
from app.schemas.business import BusinessCreate, BusinessResponse, BusinessUpdate, BusinessAnalytics
from app.api.api_v1.endpoints.auth import get_current_user
import uuid

router = APIRouter()


@router.post("/register", response_model=BusinessResponse)
async def register_business(
    business_data: BusinessCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Регистрация нового бизнеса"""
    # Создаем бизнес в БД
    business = Business(
        id=str(uuid.uuid4()),
        owner_wallet=current_user.wallet_address,
        name=business_data.name,
        category=business_data.category,
        description=business_data.description,
        tokens_per_dollar=business_data.tokens_per_dollar,
        max_discount_percent=business_data.max_discount_percent
    )
    
    db.add(business)
    db.commit()
    db.refresh(business)
    
    return business


@router.get("/my", response_model=list[BusinessResponse])
async def get_my_businesses(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Получение списка бизнесов текущего пользователя"""
    businesses = db.query(Business).filter(
        Business.owner_wallet == current_user.wallet_address
    ).all()
    
    return businesses


@router.get("/{business_id}", response_model=BusinessResponse)
async def get_business(
    business_id: str,
    db: Session = Depends(get_db)
):
    """Получение информации о бизнесе"""
    business = db.query(Business).filter(
        Business.id == business_id,
        Business.is_active == True
    ).first()
    
    if not business:
        raise HTTPException(
            status_code=404,
            detail="Бизнес не найден"
        )
    
    return business


@router.put("/{business_id}", response_model=BusinessResponse)
async def update_business(
    business_id: str,
    business_update: BusinessUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Обновление настроек бизнеса"""
    business = db.query(Business).filter(
        Business.id == business_id,
        Business.owner_wallet == current_user.wallet_address
    ).first()
    
    if not business:
        raise HTTPException(
            status_code=404,
            detail="Бизнес не найден"
        )
    
    # Обновляем поля
    update_data = business_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(business, field, value)
    
    db.commit()
    db.refresh(business)
    
    return business


@router.get("/{business_id}/analytics", response_model=BusinessAnalytics)
async def get_business_analytics(
    business_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Аналитика для бизнеса"""
    business = db.query(Business).filter(
        Business.id == business_id,
        Business.owner_wallet == current_user.wallet_address
    ).first()
    
    if not business:
        raise HTTPException(
            status_code=404,
            detail="Бизнес не найден"
        )
    
    # Здесь будет реальная аналитика
    # Пока возвращаем заглушку
    analytics = BusinessAnalytics(
        active_customers=0,
        tokens_issued=0,
        tokens_redeemed=0,
        total_transactions=0,
        roi_percentage=0.0,
        transactions_chart=[],
        customer_segments={}
    )
    
    return analytics


@router.get("/", response_model=list[BusinessResponse])
async def get_all_businesses(
    category: str = None,
    db: Session = Depends(get_db)
):
    """Получение списка всех активных бизнесов"""
    query = db.query(Business).filter(Business.is_active == True)
    
    if category:
        query = query.filter(Business.category == category)
    
    businesses = query.all()
    return businesses
