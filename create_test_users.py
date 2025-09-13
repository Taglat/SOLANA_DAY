#!/usr/bin/env python3
"""
Скрипт для создания тестовых пользователей и демонстрации системы
"""

import requests
import json
import time
from datetime import datetime

API_BASE = "http://127.0.0.1:8001/api/v1"

def create_test_user(wallet_address, name):
    """Создать тестового пользователя"""
    print(f"👤 Создаем пользователя: {name}")
    print(f"   Кошелек: {wallet_address}")
    
    response = requests.post(f"{API_BASE}/register", json={
        "wallet_address": wallet_address
    })
    
    if response.status_code == 200:
        print(f"   ✅ Пользователь создан")
        return True
    else:
        print(f"   ❌ Ошибка: {response.text}")
        return False

def create_test_receipt(customer_wallet, amount, business_id="demo_business_123"):
    """Создать тестовый чек"""
    print(f"🧾 Создаем чек на ${amount}")
    
    response = requests.post(f"{API_BASE}/receipts/generate", json={
        "customer_wallet": customer_wallet,
        "business_id": business_id,
        "amount_usd": amount,
        "transaction_id": f"test_{int(time.time())}"
    })
    
    if response.status_code == 200:
        receipt = response.json()
        print(f"   ✅ Чек создан: {receipt['id']}")
        return receipt
    else:
        print(f"   ❌ Ошибка: {response.text}")
        return None

def scan_receipt(qr_data, scanner_wallet):
    """Сканировать чек"""
    print(f"📱 Сканируем чек...")
    
    response = requests.post(f"{API_BASE}/receipts/scan", json={
        "qr_code_data": qr_data,
        "scanner_wallet": scanner_wallet
    })
    
    if response.status_code == 200:
        result = response.json()
        print(f"   ✅ Получено {result['tokens_earned']} токенов!")
        if result.get('nft_earned'):
            print(f"   🎉 Получен NFT: {result['nft_earned']}")
        return result
    else:
        print(f"   ❌ Ошибка: {response.text}")
        return None

def get_user_stats(wallet_address):
    """Получить статистику пользователя"""
    print(f"📊 Статистика пользователя {wallet_address[:8]}...")
    
    # Баланс токенов
    balance_response = requests.get(f"{API_BASE}/user-balance/{wallet_address}")
    if balance_response.status_code == 200:
        balance_data = balance_response.json()
        print(f"   💰 Токенов: {balance_data['balance']}")
    
    # NFT коллекция
    collection_response = requests.get(f"{API_BASE}/coffee-nft/coffee-collection/{wallet_address}")
    if collection_response.status_code == 200:
        collection = collection_response.json()
        print(f"   🖼️ NFT: {collection['owned_count']}/{collection['total_puzzles']} ({collection['completion_percentage']:.1f}%)")
        if collection['owned_puzzles']:
            print(f"   📋 Собрано: {', '.join([p['name'] for p in collection['owned_puzzles']])}")

def main():
    print("🚀 Создание тестовых пользователей Coffee Loyalty")
    print("=" * 50)
    
    # Тестовые пользователи
    test_users = [
        {
            "wallet": "9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM",
            "name": "Алиса (VIP клиент)"
        },
        {
            "wallet": "7Xy9K2mN8pQ4rS6tU1vW3xY5zA7bC9dE2fG4hI6jK8lM",
            "name": "Боб (новичок)"
        },
        {
            "wallet": "3FgH5iJ9kL2mN6oP8qR1sT4uV7wX0yZ3aB5cD8eF1gH4iJ",
            "name": "Каролина (коллекционер)"
        },
        {
            "wallet": "1AbC3dE5fG7hI9jK2lM4nO6pQ8rS0tU3vW5xY7zA9bC1dE",
            "name": "Дмитрий (постоянный клиент)"
        }
    ]
    
    # Создаем пользователей
    print("\n📝 Создание пользователей...")
    for user in test_users:
        create_test_user(user["wallet"], user["name"])
        time.sleep(0.5)
    
    print("\n" + "=" * 50)
    print("🎯 Тестовые сценарии")
    print("=" * 50)
    
    # Сценарий 1: Алиса - VIP клиент (много покупок)
    print("\n👑 Сценарий 1: Алиса - VIP клиент")
    alice_wallet = test_users[0]["wallet"]
    
    # Несколько покупок
    purchases = [15.50, 25.00, 45.00, 60.00]
    for amount in purchases:
        receipt = create_test_receipt(alice_wallet, amount)
        if receipt:
            scan_receipt(receipt["qr_code_data"], alice_wallet)
            time.sleep(0.5)
    
    get_user_stats(alice_wallet)
    
    # Сценарий 2: Боб - новичок (маленькая покупка)
    print("\n🆕 Сценарий 2: Боб - новичок")
    bob_wallet = test_users[1]["wallet"]
    
    receipt = create_test_receipt(bob_wallet, 8.75)
    if receipt:
        scan_receipt(receipt["qr_code_data"], bob_wallet)
    
    get_user_stats(bob_wallet)
    
    # Сценарий 3: Каролина - коллекционер (средние покупки)
    print("\n🎨 Сценарий 3: Каролина - коллекционер")
    carol_wallet = test_users[2]["wallet"]
    
    purchases = [30.00, 35.00, 40.00]
    for amount in purchases:
        receipt = create_test_receipt(carol_wallet, amount)
        if receipt:
            scan_receipt(receipt["qr_code_data"], carol_wallet)
            time.sleep(0.5)
    
    get_user_stats(carol_wallet)
    
    # Сценарий 4: Дмитрий - постоянный клиент (регулярные покупки)
    print("\n☕ Сценарий 4: Дмитрий - постоянный клиент")
    dmitry_wallet = test_users[3]["wallet"]
    
    purchases = [12.00, 18.50, 22.00, 28.00, 32.50]
    for amount in purchases:
        receipt = create_test_receipt(dmitry_wallet, amount)
        if receipt:
            scan_receipt(receipt["qr_code_data"], dmitry_wallet)
            time.sleep(0.5)
    
    get_user_stats(dmitry_wallet)
    
    print("\n" + "=" * 50)
    print("📊 Итоговая статистика всех пользователей")
    print("=" * 50)
    
    for user in test_users:
        print(f"\n👤 {user['name']}")
        get_user_stats(user["wallet"])
    
    print("\n🎉 Тестовые пользователи созданы!")
    print("\n📱 Теперь можете тестировать с телефона:")
    print("   • Откройте http://10.25.0.47:3000")
    print("   • Подключите любой из тестовых кошельков")
    print("   • Или создайте QR-код для тестирования")

if __name__ == "__main__":
    main()
