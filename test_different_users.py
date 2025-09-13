#!/usr/bin/env python3
"""
Скрипт для тестирования системы с разными пользователями
"""

import requests
import json
import time

API_BASE = "http://127.0.0.1:8001/api/v1"

# Тестовые пользователи
TEST_USERS = {
    "alice": {
        "wallet": "9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM",
        "name": "Алиса",
        "type": "VIP клиент",
        "emoji": "👑"
    },
    "bob": {
        "wallet": "7Xy9K2mN8pQ4rS6tU1vW3xY5zA7bC9dE2fG4hI6jK8lM",
        "name": "Боб",
        "type": "новичок",
        "emoji": "🆕"
    },
    "carol": {
        "wallet": "3FgH5iJ9kL2mN6oP8qR1sT4uV7wX0yZ3aB5cD8eF1gH4iJ",
        "name": "Каролина",
        "type": "коллекционер",
        "emoji": "🎨"
    },
    "dmitry": {
        "wallet": "1AbC3dE5fG7hI9jK2lM4nO6pQ8rS0tU3vW5xY7zA9bC1dE",
        "name": "Дмитрий",
        "type": "постоянный клиент",
        "emoji": "☕"
    }
}

def test_user_login(user_key):
    """Тестировать вход пользователя"""
    user = TEST_USERS[user_key]
    print(f"\n{user['emoji']} Тестируем вход: {user['name']} ({user['type']})")
    print(f"   Кошелек: {user['wallet'][:12]}...{user['wallet'][-8:]}")
    
    # Получаем баланс (это автоматически создаст пользователя если его нет)
    try:
        balance_response = requests.get(f"{API_BASE}/user-balance/{user['wallet']}")
        if balance_response.status_code == 200:
            balance_data = balance_response.json()
            print(f"   💰 Токенов: {balance_data['balance']}")
        else:
            print(f"   ❌ Ошибка получения баланса")
            return False
    except Exception as e:
        print(f"   ❌ Ошибка: {e}")
        return False
    
    # Получаем NFT коллекцию
    try:
        collection_response = requests.get(f"{API_BASE}/coffee-nft/coffee-collection/{user['wallet']}")
        if collection_response.status_code == 200:
            collection = collection_response.json()
            print(f"   🖼️ NFT: {collection['owned_count']}/{collection['total_puzzles']} ({collection['completion_percentage']:.1f}%)")
            
            if collection['owned_puzzles']:
                nft_names = [p['name'] for p in collection['owned_puzzles']]
                print(f"   📋 Собрано: {', '.join(nft_names)}")
            else:
                print(f"   📋 Собрано: нет NFT")
        else:
            print(f"   ❌ Ошибка получения коллекции")
            return False
    except Exception as e:
        print(f"   ❌ Ошибка: {e}")
        return False
    
    return True

def test_purchase_flow(user_key, amount):
    """Тестировать процесс покупки"""
    user = TEST_USERS[user_key]
    print(f"\n🛒 {user['name']} делает покупку на ${amount}")
    
    # Создаем чек
    try:
        receipt_response = requests.post(f"{API_BASE}/receipts/generate", json={
            "customer_wallet": user['wallet'],
            "business_id": "demo_business_123",
            "amount_usd": amount,
            "transaction_id": f"test_{user_key}_{int(time.time())}"
        })
        
        if receipt_response.status_code == 200:
            receipt = receipt_response.json()
            print(f"   ✅ Чек создан: {receipt['id'][:8]}...")
        else:
            print(f"   ❌ Ошибка создания чека: {receipt_response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Ошибка: {e}")
        return False
    
    # Сканируем чек
    try:
        scan_response = requests.post(f"{API_BASE}/receipts/scan", json={
            "qr_code_data": receipt['qr_code_data'],
            "scanner_wallet": user['wallet']
        })
        
        if scan_response.status_code == 200:
            result = scan_response.json()
            print(f"   🎉 Получено {result['tokens_earned']} токенов!")
            if result.get('nft_earned'):
                print(f"   🖼️ Получен NFT: {result['nft_earned']}")
            return True
        else:
            print(f"   ❌ Ошибка сканирования: {scan_response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Ошибка: {e}")
        return False

def main():
    print("🧪 Тестирование системы с разными пользователями")
    print("=" * 60)
    
    # Тестируем вход всех пользователей
    print("\n📱 Тестирование входа пользователей")
    print("-" * 40)
    
    for user_key in TEST_USERS:
        test_user_login(user_key)
        time.sleep(0.5)
    
    # Тестируем покупки
    print("\n🛒 Тестирование покупок")
    print("-" * 40)
    
    # Алиса - большая покупка
    test_purchase_flow("alice", 75.00)
    time.sleep(0.5)
    
    # Боб - маленькая покупка
    test_purchase_flow("bob", 12.50)
    time.sleep(0.5)
    
    # Каролина - средняя покупка
    test_purchase_flow("carol", 35.00)
    time.sleep(0.5)
    
    # Дмитрий - регулярная покупка
    test_purchase_flow("dmitry", 20.00)
    time.sleep(0.5)
    
    # Финальная статистика
    print("\n📊 Финальная статистика")
    print("-" * 40)
    
    for user_key in TEST_USERS:
        test_user_login(user_key)
        time.sleep(0.5)
    
    print("\n" + "=" * 60)
    print("🎯 Тестирование завершено!")
    print("\n📱 Для тестирования с телефона:")
    print("   1. Откройте http://10.25.0.47:3000")
    print("   2. Выберите пользователя из списка:")
    for user_key, user in TEST_USERS.items():
        print(f"      • {user['emoji']} {user['name']} ({user['type']})")
        print(f"        Кошелек: {user['wallet']}")
    print("   3. Или создайте QR-код для тестирования")

if __name__ == "__main__":
    main()
