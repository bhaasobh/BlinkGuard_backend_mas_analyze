import os

from fastapi import FastAPI

from app.config import INTERNAL_API_KEY, logger
from app.routes.analysis_routes import router as analysis_router
from app.routes.health_routes import router as health_router


app = FastAPI(
    title="Spam & Phishing Analysis Server by Blinkguard",
    description="A server to analyze messages for spam and phishing risks using ML and psychological factors.",
    version="1.0.0",
)
logger.info("FastAPI app created")

app.include_router(health_router)
app.include_router(analysis_router)


@app.on_event("startup")
async def startup_log():
    logger.info("FastAPI startup event fired")
    logger.info("PORT env raw value: %s", os.getenv("PORT"))
    logger.info("MONGO_URI configured: %s", bool(os.getenv("MONGO_URI")))
    logger.info("INTERNAL_API_KEY configured: %s", bool(INTERNAL_API_KEY))
