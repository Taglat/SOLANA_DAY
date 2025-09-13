# 🖼️ NFT Картинки для коллекции кофейни

## Структура папок

```
nft_pictures/
├── coffee_beans/          # Коллекция 1: Coffee Beans
│   ├── coffee_bean_1.svg
│   ├── coffee_bean_2.svg
│   └── coffee_bean_3.svg
├── espresso/              # Коллекция 2: Espresso
│   ├── espresso_1.svg
│   ├── espresso_2.svg
│   └── espresso_3.svg
├── latte_art/             # Коллекция 3: Latte Art
│   ├── latte_art_1.svg
│   ├── latte_art_2.svg
│   └── latte_art_3.svg
└── README.md
```

## Как добавить ваши картинки:

### 1. **Подготовьте картинки**
- Формат: SVG (рекомендуется) или PNG
- Размер: 200x200 пикселей или больше
- Стиль: В тематике кофейни

### 2. **Разместите картинки по папкам**

#### Coffee Beans Collection (3 картинки):
- `coffee_bean_1.svg` - Первая покупка (common)
- `coffee_bean_2.svg` - 2 покупки (common) 
- `coffee_bean_3.svg` - 3 покупки (rare)

#### Espresso Collection (3 картинки):
- `espresso_1.svg` - $25 потрачено (common)
- `espresso_2.svg` - $50 потрачено (rare)
- `espresso_3.svg` - $100 потрачено (epic)

#### Latte Art Collection (3 картинки):
- `latte_art_1.svg` - 5 покупок + $75 (rare)
- `latte_art_2.svg` - 7 покупок + $150 (epic)
- `latte_art_3.svg` - 10 покупок + $250 (legendary)

### 3. **Примеры названий файлов:**
```
coffee_beans/
├── coffee_bean_1.svg      # Простая кофейная фасоль
├── coffee_bean_2.svg      # Кофейная фасоль с листьями
└── coffee_bean_3.svg      # Золотая кофейная фасоль

espresso/
├── espresso_1.svg         # Простая чашка эспрессо
├── espresso_2.svg         # Эспрессо с пенкой
└── espresso_3.svg         # Эспрессо с декорацией

latte_art/
├── latte_art_1.svg        # Простое латте-арт
├── latte_art_2.svg        # Сложное латте-арт
└── latte_art_3.svg        # Мастерское латте-арт
```

### 4. **После добавления картинок:**
1. Перезапустите backend сервер
2. Вызовите API для инициализации коллекции:
   ```bash
   curl -X POST "http://localhost:8000/api/v1/coffee-nft/init-coffee-collection"
   ```
3. Обновите клиентское приложение

## Требования к картинкам:
- ✅ Формат: SVG, PNG, JPG
- ✅ Размер: минимум 200x200px
- ✅ Стиль: в тематике кофейни
- ✅ Уникальность: каждая картинка должна быть уникальной
- ✅ Качество: четкие, красивые изображения

## Редкость картинок:
- 🟢 **Common** - легко получить
- 🟡 **Rare** - требует больше активности
- 🟠 **Epic** - требует значительных трат
- 🔴 **Legendary** - очень сложно получить
