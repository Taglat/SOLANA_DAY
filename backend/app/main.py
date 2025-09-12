from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.api_v1.api import router as api_router
from app.db.session import engine
from app.db.base import Base

app = FastAPI(
    title="Loyalty Platform API",
    version="0.1.0",
    description="Мультибрендовая платформа лояльности"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}


app.include_router(api_router, prefix="/api/v1")


@app.on_event("startup")
async def on_startup() -> None:
    Base.metadata.create_all(bind=engine)


