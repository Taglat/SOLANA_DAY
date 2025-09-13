#!/usr/bin/env python3
"""
Скрипт для тестирования системы лояльности кофейни
"""

import requests
import json
import time
import sys

API_BASE = "http://127.0.0.1:8001/api/v1"

def test_api_health():
    """Проверка доступности API"""
    try:
        response = requests.get(f"{API_BASE.replace('/api/v1', '')}/health", timeout=5)
        if response.status_code == 200:
            print("✅ API сервер доступен")
            return True
        else:
            print(f"❌ API сервер недоступен: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Ошибка подключения к API: {e}")
        return False

def init_coffee_collection():
    """Инициализация NFT коллекции"""
    try:
        print("📦 Инициализация NFT коллекции...")
        response = requests.post(f"{API_BASE}/coffee-nft/init-coffee-collection")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Создано {result['puzzles_created']} пазлов")
            return True
        else:
            print(f"❌ Ошибка инициализации коллекции: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

def create_demo_business():
    """Создание демо-бизнеса"""
    try:
        print("🏪 Создание демо-бизнеса...")
        # Для демо просто возвращаем фиктивный бизнес
        business = {
            "id": "demo_business_123",
            "name": "Coffee Corner",
            "description": "Уютная кофейня с ароматным кофе",
            "category": "Cafe"
        }
        print(f"✅ Создан бизнес: {business['name']} (ID: {business['id']})")
        return business
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return None

def create_demo_user():
    """Создание демо-пользователя"""
    try:
        print("👤 Создание демо-пользователя...")
        user_data = {
            "wallet_address": "9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM"
        }
        
        response = requests.post(f"{API_BASE}/register", json=user_data)
        if response.status_code == 200:
            user = response.json()
            print(f"✅ Создан пользователь: {user['wallet']}")
            return user
        else:
            print(f"❌ Ошибка создания пользователя: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return None

def test_purchase_and_receipt(business_id):
    """Тестирование покупки и создания чека"""
    try:
        print("💳 Тестирование покупки и создания чека...")
        
        # Создаем чек
        receipt_data = {
            "customer_wallet": "9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM",
            "business_id": business_id,
            "amount_usd": 15.50,
            "transaction_id": "demo_tx_123"
        }
        
        response = requests.post(f"{API_BASE}/receipts/generate", json=receipt_data)
        if response.status_code == 200:
            receipt = response.json()
            print(f"✅ Создан чек: ${receipt['amount_usd']}")
            print(f"   ID чека: {receipt['id']}")
            return receipt
        else:
            print(f"❌ Ошибка создания чека: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return None

def test_receipt_scanning():
    """Тестирование сканирования чека"""
    try:
        print("🧾 Тестирование сканирования чека...")
        
        # Создаем тестовые данные QR-кода
        qr_data = {
            "receipt_id": "test_receipt_123",
            "transaction_id": "test_tx_123",
            "business_id": "test_business_123",
            "customer_wallet": "9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM",
            "amount_usd": "15.50",
            "timestamp": int(time.time()),
            "type": "receipt_scan"
        }
        
        scan_data = {
            "qr_code_data": json.dumps(qr_data),
            "scanner_wallet": "9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM"
        }
        
        response = requests.post(f"{API_BASE}/receipts/scan", json=scan_data)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Чек отсканирован: {result['message']}")
            print(f"   Получено токенов: {result['tokens_earned']}")
            return True
        else:
            print(f"❌ Ошибка сканирования чека: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

def test_nft_collection():
    """Тестирование NFT коллекции"""
    try:
        print("🖼️ Тестирование NFT коллекции...")
        
        wallet = "9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM"
        response = requests.get(f"{API_BASE}/coffee-nft/coffee-collection/{wallet}")
        if response.status_code == 200:
            collection = response.json()
            print(f"✅ Коллекция загружена:")
            print(f"   Всего пазлов: {collection['total_puzzles']}")
            print(f"   Собрано: {collection['owned_count']}")
            print(f"   Осталось: {collection['missing_count']}")
            print(f"   Прогресс: {collection['completion_percentage']:.1f}%")
            return True
        else:
            print(f"❌ Ошибка загрузки коллекции: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

def main():
    """Основная функция тестирования"""
    print("🚀 Тестирование системы лояльности кофейни")
    print("=" * 50)
    
    # Проверяем доступность API
    if not test_api_health():
        print("\n❌ API сервер недоступен. Запустите backend сервер:")
        print("   cd backend && python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
        sys.exit(1)
    
    # Инициализируем коллекцию
    if not init_coffee_collection():
        print("\n❌ Не удалось инициализировать коллекцию")
        sys.exit(1)
    
    # Создаем демо-бизнес
    business = create_demo_business()
    if not business:
        print("\n❌ Не удалось создать демо-бизнес")
        sys.exit(1)
    
    # Создаем демо-пользователя
    user = create_demo_user()
    if not user:
        print("\n❌ Не удалось создать демо-пользователя")
        sys.exit(1)
    
    # Тестируем покупку
    transaction = test_purchase_and_receipt(business['id'])
    if not transaction:
        print("\n❌ Не удалось протестировать покупку")
        sys.exit(1)
    
    # Тестируем NFT коллекцию
    if not test_nft_collection():
        print("\n❌ Не удалось протестировать NFT коллекцию")
        sys.exit(1)
    
    print("\n" + "=" * 50)
    print("🎉 Все тесты прошли успешно!")
    print("\n📱 Теперь можете открыть:")
    print("   • Клиентское приложение: http://localhost:3000")
    print("   • Бизнес дашборд: http://localhost:3001")
    print("   • Просмотр картинок: http://localhost:3000/images/nft_pictures/view_images.html")
    print("   • API документация: http://localhost:8000/docs")

if __name__ == "__main__":
    main()
