from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse, UserLogin
from app.services.solana_service import SolanaService
from app.core.config import settings
import jwt
import uuid

router = APIRouter()
solana_service = SolanaService()

# OAuth2 схема
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


@router.post("/register", response_model=UserResponse)
async def register_user(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """Регистрация нового пользователя"""
    # Проверяем, существует ли пользователь
    existing_user = db.query(User).filter(
        User.wallet_address == user_data.wallet_address
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Пользователь с таким кошельком уже существует"
        )
    
    # Создаем Associated Token Account
    token_account = await solana_service.create_associated_token_account(
        user_data.wallet_address
    )
    
    # Создаем пользователя в БД
    user = User(
        id=str(uuid.uuid4()),
        username=user_data.username,
        email=user_data.email,
        wallet_address=user_data.wallet_address,
        token_account=token_account
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return user


@router.post("/login", response_model=dict)
async def login_user(
    login_data: UserLogin,
    db: Session = Depends(get_db)
):
    """Аутентификация пользователя через Solana подпись"""
    # Валидация подписи (упрощенная версия)
    # В реальном проекте нужно проверить подпись через Solana
    
    user = db.query(User).filter(
        User.wallet_address == login_data.wallet_address
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=404,
            detail="Пользователь не найден"
        )
    
    # Обновляем время последнего входа
    user.last_login = db.func.now()
    db.commit()
    
    # Создаем JWT токен
    token_data = {
        "user_id": user.id,
        "wallet_address": user.wallet_address
    }
    
    access_token = jwt.encode(
        token_data,
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserResponse.from_orm(user)
    }


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """Получение текущего пользователя из JWT токена"""
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm]
        )
        user_id = payload.get("user_id")
        
        if user_id is None:
            raise HTTPException(
                status_code=401,
                detail="Неверный токен"
            )
        
        user = db.query(User).filter(User.id == user_id).first()
        if user is None:
            raise HTTPException(
                status_code=404,
                detail="Пользователь не найден"
            )
        
        return user
        
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=401,
            detail="Неверный токен"
        )


@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: User = Depends(get_current_user)
):
    """Получение информации о текущем пользователе"""
    return current_user
