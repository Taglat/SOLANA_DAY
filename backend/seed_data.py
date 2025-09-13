#!/usr/bin/env python3
"""
Скрипт для создания демо-данных в базе данных
"""
import asyncio
import sys
import os

# Добавляем путь к приложению
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.session import SessionLocal
from app.models.user import User
from app.models.business import Business
from app.models.transaction import Transaction
from decimal import Decimal
import uuid
from datetime import datetime, timedelta
import random

def create_demo_data():
    """Создание демо-данных"""
    db = SessionLocal()
    
    try:
        # Создаем демо-пользователей
        users = [
            User(
                id=str(uuid.uuid4()),
                username="alice_crypto",
                email="alice@example.com",
                wallet_address="9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM",
                token_account="ATA44DXMX4LZKE8YEVD2GBYAVOMSRIRARZF",
                is_active=True,
                created_at=datetime.now() - timedelta(days=30)
            ),
            User(
                id=str(uuid.uuid4()),
                username="bob_trader",
                email="bob@example.com", 
                wallet_address="7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU",
                token_account="ATB55EYNX5MZKE9ZFWD3HCYBVPMTRIRARZF",
                is_active=True,
                created_at=datetime.now() - timedelta(days=25)
            ),
            User(
                id=str(uuid.uuid4()),
                username="charlie_coffee",
                email="charlie@example.com",
                wallet_address="5Q544fKrFoe6tsEbD7S8EmxGTJYAKtTVhAW5Q5pge4j1",
                token_account="ATC66FZOY6NZKE0AGXE4IDYBVQNTRIRARZF",
                is_active=True,
                created_at=datetime.now() - timedelta(days=20)
            )
        ]
        
        for user in users:
            db.add(user)
        
        # Создаем демо-бизнесы
        businesses = [
            Business(
                id=str(uuid.uuid4()),
                owner_wallet="9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM",
                name="Coffee Corner",
                category="Cafe",
                description="Лучший кофе в городе с уютной атмосферой",
                tokens_per_dollar=10,
                max_discount_percent=30,
                is_active=True,
                created_at=datetime.now() - timedelta(days=30)
            ),
            Business(
                id=str(uuid.uuid4()),
                owner_wallet="7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU",
                name="Elite Barbershop",
                category="Barbershop",
                description="Премиальная стрижка и уход за бородой",
                tokens_per_dollar=15,
                max_discount_percent=50,
                is_active=True,
                created_at=datetime.now() - timedelta(days=25)
            ),
            Business(
                id=str(uuid.uuid4()),
                owner_wallet="5Q544fKrFoe6tsEbD7S8EmxGTJYAKtTVhAW5Q5pge4j1",
                name="FitLife Gym",
                category="Fitness",
                description="Современный фитнес-клуб с новейшим оборудованием",
                tokens_per_dollar=5,
                max_discount_percent=20,
                is_active=True,
                created_at=datetime.now() - timedelta(days=20)
            )
        ]
        
        for business in businesses:
            db.add(business)
        
        db.commit()
        
        # Получаем созданные записи
        created_users = db.query(User).all()
        created_businesses = db.query(Business).all()
        
        # Создаем демо-транзакции
        transactions = []
        
        # Транзакции для Coffee Corner
        coffee_business = created_businesses[0]
        for i in range(15):
            user = random.choice(created_users)
            amount = Decimal(str(round(random.uniform(3.0, 15.0), 2)))
            tokens = int(amount * coffee_business.tokens_per_dollar)
            
            transaction = Transaction(
                id=str(uuid.uuid4()),
                customer_wallet=user.wallet_address,
                business_id=coffee_business.id,
                transaction_type="EARN",
                amount_usd=amount,
                tokens_amount=tokens,
                solana_signature=f"mint_{random.randint(100000, 999999)}",
                created_at=datetime.now() - timedelta(days=random.randint(1, 30))
            )
            transactions.append(transaction)
        
        # Транзакции для Elite Barbershop
        barbershop_business = created_businesses[1]
        for i in range(12):
            user = random.choice(created_users)
            amount = Decimal(str(round(random.uniform(20.0, 80.0), 2)))
            tokens = int(amount * barbershop_business.tokens_per_dollar)
            
            transaction = Transaction(
                id=str(uuid.uuid4()),
                customer_wallet=user.wallet_address,
                business_id=barbershop_business.id,
                transaction_type="EARN",
                amount_usd=amount,
                tokens_amount=tokens,
                solana_signature=f"mint_{random.randint(100000, 999999)}",
                created_at=datetime.now() - timedelta(days=random.randint(1, 25))
            )
            transactions.append(transaction)
        
        # Транзакции для FitLife Gym
        gym_business = created_businesses[2]
        for i in range(8):
            user = random.choice(created_users)
            amount = Decimal(str(round(random.uniform(50.0, 150.0), 2)))
            tokens = int(amount * gym_business.tokens_per_dollar)
            
            transaction = Transaction(
                id=str(uuid.uuid4()),
                customer_wallet=user.wallet_address,
                business_id=gym_business.id,
                transaction_type="EARN",
                amount_usd=amount,
                tokens_amount=tokens,
                solana_signature=f"mint_{random.randint(100000, 999999)}",
                created_at=datetime.now() - timedelta(days=random.randint(1, 20))
            )
            transactions.append(transaction)
        
        # Несколько транзакций скидок
        for i in range(5):
            user = random.choice(created_users)
            business = random.choice(created_businesses)
            tokens_used = random.randint(50, 200)
            discount_amount = Decimal(str(round(tokens_used / 10, 2)))
            
            transaction = Transaction(
                id=str(uuid.uuid4()),
                customer_wallet=user.wallet_address,
                business_id=business.id,
                transaction_type="REDEEM",
                amount_usd=discount_amount,
                tokens_amount=tokens_used,
                solana_signature=f"burn_{random.randint(100000, 999999)}",
                created_at=datetime.now() - timedelta(days=random.randint(1, 15))
            )
            transactions.append(transaction)
        
        for transaction in transactions:
            db.add(transaction)
        
        db.commit()
        
        print("✅ Демо-данные успешно созданы!")
        print(f"👥 Пользователи: {len(created_users)}")
        print(f"🏪 Бизнесы: {len(created_businesses)}")
        print(f"💳 Транзакции: {len(transactions)}")
        
    except Exception as e:
        print(f"❌ Ошибка создания демо-данных: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_demo_data()
