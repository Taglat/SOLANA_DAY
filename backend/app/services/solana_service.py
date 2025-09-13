from app.core.config import settings
import asyncio
import random
import string


class SolanaService:
    def __init__(self) -> None:
        # Для MVP используем заглушки вместо реальных Solana операций
        self.loyalty_token_mint = "LoTyTokn111111111111111111111111111111111"

    async def create_associated_token_account(self, user_wallet: str) -> str:
        """Создание Associated Token Account для пользователя (заглушка)"""
        # В MVP просто возвращаем сгенерированный адрес
        await asyncio.sleep(0.1)  # Имитируем сетевую задержку
        return f"ATA{''.join(random.choices(string.ascii_uppercase + string.digits, k=32))}"

    async def mint_loyalty_tokens(self, user_wallet: str, amount: int, business_id: str) -> str:
        """Выдача токенов лояльности (заглушка)"""
        # В MVP просто возвращаем поддельную подпись транзакции
        await asyncio.sleep(0.2)  # Имитируем время обработки
        return f"mint_{''.join(random.choices(string.ascii_lowercase + string.digits, k=44))}"

    async def burn_tokens_for_discount(self, user_wallet: str, amount: int) -> str:
        """Сжигание токенов для получения скидки (заглушка)"""
        # В MVP просто возвращаем поддельную подпись транзакции
        await asyncio.sleep(0.2)  # Имитируем время обработки
        return f"burn_{''.join(random.choices(string.ascii_lowercase + string.digits, k=44))}"

    async def get_token_balance(self, user_wallet: str) -> int:
        """Получение баланса токенов пользователя (заглушка)"""
        # В MVP возвращаем случайный баланс для демонстрации
        await asyncio.sleep(0.1)
        return random.randint(0, 1000)

    async def get_sol_balance(self, wallet_address: str) -> float:
        """Получение баланса SOL кошелька (заглушка)"""
        # В MVP возвращаем случайный баланс для демонстрации
        await asyncio.sleep(0.1)
        return round(random.uniform(0.1, 5.0), 2)