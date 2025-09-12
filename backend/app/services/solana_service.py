from solana.rpc.async_api import AsyncClient
from solana.keypair import Keypair

from app.core.config import settings


class SolanaService:
    def __init__(self) -> None:
        self.client = AsyncClient(settings.solana_rpc_url)
        self.payer = Keypair()  # Replace with a persistent key in production

    async def create_associated_token_account(self, user_wallet: str) -> str | None:
        # TODO: implement via anchorpy or spl-token equivalent
        return None

    async def mint_loyalty_tokens(self, user_wallet: str, amount: int, business_id: str) -> str | None:
        # TODO: call Anchor program
        return None

    async def burn_tokens_for_discount(self, user_wallet: str, amount: int) -> str | None:
        # TODO: call Anchor program
        return None

    async def get_token_balance(self, user_wallet: str) -> int:
        # TODO: query token account
        return 0


