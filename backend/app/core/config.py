from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg2://user:pass@localhost:5432/loyalty"
    redis_url: str = "redis://localhost:6379/0"
    solana_rpc_url: str = "https://api.devnet.solana.com"
    jwt_secret: str = "change-me"
    jwt_algorithm: str = "HS256"

    class Config:
        env_file = ".env"
        env_prefix = ""


settings = Settings()


