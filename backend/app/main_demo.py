from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.api_v1.demo_api import router as demo_router

# Demo version - no database needed

app = FastAPI(
    title="Coffee Loyalty API - Demo",
    description="API для системы лояльности кофейни (демо версия без базы данных)",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include demo API router
app.include_router(demo_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "Coffee Loyalty API - Demo", "status": "running", "database": "In-Memory"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "API is running", "database": "In-Memory"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)