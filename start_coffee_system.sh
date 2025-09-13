#!/bin/bash

# Скрипт для запуска системы лояльности кофейни

echo "🚀 Запуск системы лояльности кофейни"
echo "=================================="

# Проверяем, что мы в правильной директории
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ Запустите скрипт из корневой папки проекта"
    exit 1
fi

# Функция для проверки порта
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null ; then
        echo "✅ Порт $1 уже занят"
        return 0
    else
        echo "❌ Порт $1 свободен"
        return 1
    fi
}

# Проверяем доступность портов
echo "🔍 Проверка портов..."
check_port 8000
check_port 3000
check_port 3001

# Запускаем backend
echo ""
echo "🔧 Запуск backend сервера..."
if ! check_port 8000; then
    echo "Запускаем backend на порту 8000..."
    cd backend
    python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
    BACKEND_PID=$!
    cd ..
    echo "Backend запущен с PID: $BACKEND_PID"
else
    echo "Backend уже запущен"
fi

# Ждем запуска backend
echo "⏳ Ожидание запуска backend..."
sleep 5

# Инициализируем систему
echo ""
echo "📦 Инициализация NFT коллекции..."
python test_coffee_system.py

# Запускаем frontend клиента
echo ""
echo "👤 Запуск клиентского приложения..."
if ! check_port 3000; then
    echo "Запускаем клиентское приложение на порту 3000..."
    cd frontend_client
    python -m http.server 3000 &
    CLIENT_PID=$!
    cd ..
    echo "Клиентское приложение запущено с PID: $CLIENT_PID"
else
    echo "Клиентское приложение уже запущено"
fi

# Запускаем бизнес дашборд
echo ""
echo "🏪 Запуск бизнес дашборда..."
if ! check_port 3001; then
    echo "Запускаем бизнес дашборд на порту 3001..."
    cd frontend_seller
    python -m http.server 3001 &
    SELLER_PID=$!
    cd ..
    echo "Бизнес дашборд запущен с PID: $SELLER_PID"
else
    echo "Бизнес дашборд уже запущен"
fi

echo ""
echo "🎉 Система запущена!"
echo "==================="
echo ""
echo "📱 Доступные интерфейсы:"
echo "   • Клиентское приложение: http://localhost:3000"
echo "   • Бизнес дашборд: http://localhost:3001"
echo "   • API документация: http://localhost:8000/docs"
echo "   • Просмотр картинок: http://localhost:3000/images/nft_pictures/view_images.html"
echo ""
echo "🎮 Демо-сценарий:"
echo "   1. Откройте клиентское приложение"
echo "   2. Подключите кошелек"
echo "   3. Откройте бизнес дашборд"
echo "   4. Создайте чек для клиента"
echo "   5. Отсканируйте чек в клиентском приложении"
echo "   6. Посмотрите на NFT коллекцию!"
echo ""
echo "🛑 Для остановки системы нажмите Ctrl+C"

# Ждем сигнала завершения
trap 'echo ""; echo "🛑 Остановка системы..."; kill $BACKEND_PID $CLIENT_PID $SELLER_PID 2>/dev/null; exit 0' INT

# Ждем
wait
