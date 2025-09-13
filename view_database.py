#!/usr/bin/env python3
"""
Скрипт для просмотра состояния in-memory базы данных
"""

import requests
import json

API_BASE = "http://127.0.0.1:8001/api/v1"

def get_database_status():
    """Получить статус базы данных"""
    print("🗄️ Состояние in-memory базы данных")
    print("=" * 50)
    
    # Проверяем здоровье API
    try:
        health_response = requests.get(f"{API_BASE.replace('/api/v1', '')}/health")
        if health_response.status_code == 200:
            health_data = health_response.json()
            print(f"✅ API: {health_data['status']}")
            print(f"📊 База данных: {health_data['database']}")
        else:
            print("❌ API недоступен")
            return
    except Exception as e:
        print(f"❌ Ошибка подключения к API: {e}")
        return
    
    print("\n" + "=" * 50)
    print("👥 Пользователи в системе")
    print("=" * 50)
    
    # Тестовые кошельки
    test_wallets = [
        "9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM",  # Алиса
        "7Xy9K2mN8pQ4rS6tU1vW3xY5zA7bC9dE2fG4hI6jK8lM",  # Боб
        "3FgH5iJ9kL2mN6oP8qR1sT4uV7wX0yZ3aB5cD8eF1gH4iJ",  # Каролина
        "1AbC3dE5fG7hI9jK2lM4nO6pQ8rS0tU3vW5xY7zA9bC1dE"   # Дмитрий
    ]
    
    user_names = ["Алиса (VIP)", "Боб (новичок)", "Каролина (коллекционер)", "Дмитрий (постоянный)"]
    
    for i, wallet in enumerate(test_wallets):
        name = user_names[i] if i < len(user_names) else f"Пользователь {i+1}"
        print(f"\n👤 {name}")
        print(f"   Кошелек: {wallet[:12]}...{wallet[-8:]}")
        
        # Получаем баланс
        try:
            balance_response = requests.get(f"{API_BASE}/user-balance/{wallet}")
            if balance_response.status_code == 200:
                balance_data = balance_response.json()
                print(f"   💰 Токенов: {balance_data['balance']}")
            else:
                print(f"   ❌ Ошибка получения баланса: {balance_response.status_code}")
        except Exception as e:
            print(f"   ❌ Ошибка: {e}")
        
        # Получаем NFT коллекцию
        try:
            collection_response = requests.get(f"{API_BASE}/coffee-nft/coffee-collection/{wallet}")
            if collection_response.status_code == 200:
                collection = collection_response.json()
                print(f"   🖼️ NFT: {collection['owned_count']}/{collection['total_puzzles']} ({collection['completion_percentage']:.1f}%)")
                
                if collection['owned_puzzles']:
                    nft_names = [p['name'] for p in collection['owned_puzzles']]
                    print(f"   📋 Собрано: {', '.join(nft_names)}")
                else:
                    print(f"   📋 Собрано: нет NFT")
            else:
                print(f"   ❌ Ошибка получения коллекции: {collection_response.status_code}")
        except Exception as e:
            print(f"   ❌ Ошибка: {e}")

def get_receipts_info():
    """Получить информацию о чеках"""
    print("\n" + "=" * 50)
    print("🧾 Чеки в системе")
    print("=" * 50)
    
    try:
        receipts_response = requests.get(f"{API_BASE}/receipts/my")
        if receipts_response.status_code == 200:
            receipts = receipts_response.json()
            print(f"📊 Всего чеков: {len(receipts)}")
            
            scanned_count = sum(1 for r in receipts if r.get('is_scanned', False))
            print(f"✅ Отсканировано: {scanned_count}")
            print(f"⏳ Ожидает сканирования: {len(receipts) - scanned_count}")
            
            if receipts:
                print(f"\n📋 Последние чеки:")
                for i, receipt in enumerate(receipts[-5:]):  # Показываем последние 5
                    status = "✅ Отсканирован" if receipt.get('is_scanned', False) else "⏳ Ожидает"
                    print(f"   {i+1}. ${receipt['amount_usd']} - {status}")
        else:
            print(f"❌ Ошибка получения чеков: {receipts_response.status_code}")
    except Exception as e:
        print(f"❌ Ошибка: {e}")

def get_nft_collection_info():
    """Получить информацию о NFT коллекции"""
    print("\n" + "=" * 50)
    print("🖼️ NFT Коллекция")
    print("=" * 50)
    
    try:
        # Инициализируем коллекцию если нужно
        init_response = requests.post(f"{API_BASE}/coffee-nft/init-coffee-collection")
        if init_response.status_code == 200:
            init_data = init_response.json()
            print(f"✅ Коллекция инициализирована: {init_data['puzzles_created']} пазлов")
        else:
            print(f"❌ Ошибка инициализации коллекции: {init_response.status_code}")
    except Exception as e:
        print(f"❌ Ошибка: {e}")

def main():
    print("🔍 Просмотр состояния базы данных Coffee Loyalty")
    print("=" * 60)
    
    get_database_status()
    get_receipts_info()
    get_nft_collection_info()
    
    print("\n" + "=" * 60)
    print("💡 Информация о базе данных:")
    print("   • Тип: In-Memory (в памяти)")
    print("   • Данные сохраняются только во время работы сервера")
    print("   • При перезапуске сервера все данные теряются")
    print("   • Подходит для демонстрации и тестирования")
    print("\n📱 Для тестирования с телефона:")
    print("   • Откройте http://10.25.0.47:3000")
    print("   • Используйте любой из тестовых кошельков")
    print("   • Или создайте QR-код для тестирования")

if __name__ == "__main__":
    main()
