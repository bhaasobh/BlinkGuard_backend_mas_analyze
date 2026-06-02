from fastapi import APIRouter


router = APIRouter()


@router.get("/")
async def root():
    return {"message": "Spam & Phishing Analysis Server is running. Use POST /analyze to analyze messages."}
