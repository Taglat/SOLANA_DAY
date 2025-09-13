# ☕ Система лояльности кофейни - MVP

## 🎯 Описание проекта

Полнофункциональная система лояльности для кофейни с NFT коллекцией, где клиенты получают чеки с QR-кодами, сканируют их в приложении и получают токены лояльности + NFT картинки для коллекции.

## ✨ Основные функции

### **Для клиентов:**
- 🧾 Получение чеков с QR-кодами при покупке
- 📱 Сканирование чеков в мобильном приложении
- 🪙 Начисление токенов лояльности
- 🖼️ Сбор NFT коллекции из 9 картинок
- 🏆 Система достижений
- 📊 Просмотр истории транзакций

### **Для бизнеса:**
- 🏪 Генерация чеков с QR-кодами
- 📊 Аналитика и статистика
- ⚙️ Настройка программы лояльности
- 📱 Сканер QR-кодов

## 🚀 Быстрый запуск

### **Автоматический запуск:**
```bash
./start_coffee_system.sh
```

### **Ручной запуск:**
```bash
# 1. Запуск backend
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 2. Запуск клиентского приложения
cd frontend_client
python -m http.server 3000

# 3. Запуск бизнес дашборда
cd frontend_seller
python -m http.server 3001

# 4. Инициализация системы
python test_coffee_system.py
```

## 📱 Доступные интерфейсы

- **Клиентское приложение:** http://localhost:3000
- **Бизнес дашборд:** http://localhost:3001
- **API документация:** http://localhost:8000/docs
- **Просмотр картинок:** http://localhost:3000/images/nft_pictures/view_images.html

## 🎮 Демо-сценарий

1. **Откройте клиентское приложение** (http://localhost:3000)
2. **Подключите кошелек** (нажмите кнопку)
3. **Откройте бизнес дашборд** (http://localhost:3001)
4. **Войдите в систему** (нажмите кнопку)
5. **Создайте чек:**
   - Введите кошелек клиента: `9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM`
   - Введите сумму: `15.50`
   - Нажмите "Создать чек"
6. **Скопируйте QR-код** с чека
7. **Вернитесь в клиентское приложение**
8. **Отсканируйте чек:**
   - Вставьте QR данные в поле
   - Нажмите "Сканировать чек"
9. **Посмотрите на полученные токены и NFT!**

## 🖼️ NFT Коллекция

### **Coffee Beans Collection (3 картинки):**
- 🟢 **Coffee Bean 1** - Первая покупка (Common)
- 🟢 **Coffee Bean 2** - 2 покупки (Common)
- 🟡 **Coffee Bean 3** - 3 покупки (Rare)

### **Espresso Collection (3 картинки):**
- 🟢 **Espresso 1** - $25 потрачено (Common)
- 🟡 **Espresso 2** - $50 потрачено (Rare)
- 🟠 **Espresso 3** - $100 потрачено (Epic)

### **Latte Art Collection (3 картинки):**
- 🟡 **Latte Art 1** - 5 покупок + $75 (Rare)
- 🟠 **Latte Art 2** - 7 покупок + $150 (Epic)
- 🔴 **Latte Art 3** - 10 покупок + $250 (Legendary)

## 🏗️ Архитектура

### **Backend (FastAPI):**
- `app/api/api_v1/endpoints/receipts.py` - API для чеков
- `app/api/api_v1/endpoints/coffee_nft.py` - API для NFT коллекции
- `app/services/nft_service.py` - Логика NFT и достижений
- `app/models/transaction.py` - Модели чеков и транзакций

### **Frontend:**
- `frontend_client/index.html` - Клиентское приложение
- `frontend_seller/index.html` - Бизнес дашборд
- `frontend_client/images/nft_pictures/` - Картинки NFT

### **Демо и тестирование:**
- `test_coffee_system.py` - Тестирование системы
- `start_coffee_system.sh` - Скрипт запуска
- `DEMO_SCENARIO.md` - Подробный демо-сценарий

## 🔧 API Эндпоинты

### **Чеки:**
- `POST /api/v1/receipts/generate` - Генерация чека
- `POST /api/v1/receipts/scan` - Сканирование чека
- `GET /api/v1/receipts/my` - Мои чеки

### **NFT Коллекция:**
- `POST /api/v1/coffee-nft/init-coffee-collection` - Инициализация
- `GET /api/v1/coffee-nft/coffee-collection/{wallet}` - Получение коллекции

### **Транзакции:**
- `POST /api/v1/transactions/purchase` - Создание покупки
- `GET /api/v1/transactions/my` - Мои транзакции

## 🎨 Кастомизация

### **Добавление новых картинок:**
1. Добавьте картинки в `frontend_client/images/nft_pictures/`
2. Переименуйте по схеме: `collection_name_number.jpg`
3. Перезапустите backend
4. Вызовите API инициализации

### **Изменение условий достижений:**
1. Отредактируйте `backend/app/api/api_v1/endpoints/coffee_nft.py`
2. Измените условия в `achievements_data`
3. Перезапустите backend

## 🐛 Устранение неполадок

### **API недоступен:**
```bash
curl http://localhost:8000/health
```

### **Картинки не отображаются:**
```bash
curl http://localhost:3000
```

### **NFT не создаются:**
```bash
curl -X POST http://localhost:8000/api/v1/coffee-nft/init-coffee-collection
```

## 📁 Структура проекта

```
solana-1/
├── backend/                    # FastAPI backend
│   ├── app/
│   │   ├── api/api_v1/endpoints/
│   │   │   ├── receipts.py     # API чеков
│   │   │   └── coffee_nft.py   # API NFT коллекции
│   │   ├── models/
│   │   │   └── transaction.py  # Модели чеков
│   │   └── services/
│   │       └── nft_service.py  # Логика NFT
├── frontend_client/            # Клиентское приложение
│   ├── index.html
│   └── images/nft_pictures/    # Картинки NFT
│       ├── coffee_beans/       # 3 картинки
│       ├── espresso/           # 3 картинки
│       ├── latte_art/          # 3 картинки
│       └── view_images.html    # Просмотрщик
├── frontend_seller/            # Бизнес дашборд
│   └── index.html
├── test_coffee_system.py       # Тестирование
├── start_coffee_system.sh      # Скрипт запуска
└── DEMO_SCENARIO.md            # Демо-сценарий
```

## 🎉 Готово!

Система лояльности кофейни полностью готова к использованию! 

**Основные возможности:**
- ✅ Генерация чеков с QR-кодами
- ✅ Сканирование чеков клиентами
- ✅ Начисление токенов лояльности
- ✅ NFT коллекция из 9 картинок
- ✅ Система достижений
- ✅ Красивый интерфейс
- ✅ Полная документация

**Приятного использования!** ☕🎨
