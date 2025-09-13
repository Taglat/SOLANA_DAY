#!/usr/bin/env python3
"""
Скрипт для инициализации системы лояльности кофейни
"""

import requests
import json
import time

API_BASE = "http://localhost:8000/api/v1"

def init_coffee_system():
    """Инициализация системы кофейни"""
    print("🚀 Инициализация системы лояльности кофейни...")
    
    try:
        # 1. Инициализация NFT коллекции
        print("📦 Создание NFT коллекции...")
        response = requests.post(f"{API_BASE}/coffee-nft/init-coffee-collection")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Создано {result['puzzles_created']} пазлов и {result['achievements_created']} достижений")
        else:
            print(f"❌ Ошибка создания коллекции: {response.text}")
            return False
        
        # 2. Создание демо-бизнеса кофейни
        print("🏪 Создание демо-бизнеса кофейни...")
        business_data = {
            "name": "Coffee Corner",
            "description": "Уютная кофейня с ароматным кофе",
            "category": "Cafe",
            "tokens_per_dollar": 10,
            "max_discount_percent": 30,
            "owner_wallet": "9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM"
        }
        
        response = requests.post(f"{API_BASE}/business/register", json=business_data)
        if response.status_code == 200:
            business = response.json()
            print(f"✅ Создан бизнес: {business['name']} (ID: {business['id']})")
        else:
            print(f"❌ Ошибка создания бизнеса: {response.text}")
            return False
        
        # 3. Создание демо-пользователя
        print("👤 Создание демо-пользователя...")
        user_data = {
            "username": "coffee_lover",
            "email": "coffee@example.com",
            "wallet_address": "9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM"
        }
        
        response = requests.post(f"{API_BASE}/auth/register", json=user_data)
        if response.status_code == 200:
            user = response.json()
            print(f"✅ Создан пользователь: {user['username']}")
        else:
            print(f"❌ Ошибка создания пользователя: {response.text}")
            return False
        
        # 4. Создание демо-транзакций
        print("💳 Создание демо-транзакций...")
        demo_transactions = [
            {"amount_usd": 5.50, "description": "Капучино"},
            {"amount_usd": 3.25, "description": "Эспрессо"},
            {"amount_usd": 7.80, "description": "Латте с сиропом"},
            {"amount_usd": 4.20, "description": "Американо"},
            {"amount_usd": 6.90, "description": "Мокко"}
        ]
        
        for i, tx_data in enumerate(demo_transactions):
            purchase_data = {
                "customer_wallet": "9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM",
                "business_id": business['id'],
                "amount_usd": tx_data["amount_usd"]
            }
            
            response = requests.post(f"{API_BASE}/transactions/purchase", json=purchase_data)
            if response.status_code == 200:
                print(f"✅ Транзакция {i+1}: ${tx_data['amount_usd']} - {tx_data['description']}")
            else:
                print(f"❌ Ошибка транзакции {i+1}: {response.text}")
        
        print("\n🎉 Система лояльности кофейни успешно инициализирована!")
        print("\n📱 Доступные интерфейсы:")
        print("   • Клиентское приложение: http://localhost:3000")
        print("   • Бизнес дашборд: http://localhost:3001")
        print("   • API документация: http://localhost:8000/docs")
        
        print("\n🧾 Демо-сценарий:")
        print("   1. Откройте клиентское приложение")
        print("   2. Подключите кошелек")
        print("   3. Посмотрите на коллекцию NFT")
        print("   4. Откройте бизнес дашборд")
        print("   5. Создайте чек для клиента")
        print("   6. Отсканируйте чек в клиентском приложении")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка инициализации: {e}")
        return False

if __name__ == "__main__":
    init_coffee_system()
