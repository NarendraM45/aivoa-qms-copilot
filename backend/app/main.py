from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.core.config import get_settings
from app.core.database import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    await init_db()
    yield
    # shutdown

app = FastAPI(
    title="Pharma Complaint Management System",
    description="AI-powered customer complaint management for pharmaceutical QMS",
    version="1.0.0",
    lifespan=lifespan,
)

settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include ALL routers
from app.api.routes.complaints import router as complaints_router
from app.api.routes.extraction import router as extraction_router
from app.api.routes.chat import router as chat_router
from app.api.routes.ai_features import router as ai_features_router
from app.api.routes.ws import router as ws_router
from app.api.routes.copilot import router as copilot_router

app.include_router(complaints_router)
app.include_router(extraction_router)
app.include_router(chat_router)
app.include_router(ai_features_router)
app.include_router(ws_router)
app.include_router(copilot_router)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "pcms"}
