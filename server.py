from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from analyze_message import analyze_message
import os
from dotenv import load_dotenv
import uvicorn
from mongodb_handler import save_phishing_message

load_dotenv()

app = FastAPI(
    title="Spam & Phishing Analysis Server by Blinkguard",
    description="A server to analyze messages for spam and phishing risks using ML and psychological factors.",
    version="1.0.0"
)


class AnalysisRequest(BaseModel):
    message: str

class ReportRequest(BaseModel):
    message: str
    metadata: dict = None

class AnalysisResponse(BaseModel):
    message: str
    ml_prediction: str
    ml_confidence: float
    ml_risk_score: float
    final_decision: str
    risk_band: str
    final_risk_score: float
    psychology_average: float
    high_signal_count: int
    psychological_factors: list[str]
    psychology_risk_scores: dict[str, float]

@app.post("/analyze", response_model=AnalysisResponse)
async def analyze(request: AnalysisRequest):
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    
    try:
        result = analyze_message(request.message)
        
        # Save to MongoDB if it's suspicious of phishing
        if result["final_decision"] == "phishing":
            await save_phishing_message(request.message, result)

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/report")
async def report_phishing(request: ReportRequest):
    """
    Endpoint for frontend to report a phishing message directly.
    """
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    
    success = await save_phishing_message(
        request.message, 
        {"source": "frontend_report", "metadata": request.metadata}
    )
    
    if success:
        return {"status": "success", "message": "Phishing message reported and saved."}
    else:
        raise HTTPException(status_code=500, detail="Failed to save report to database.")

@app.get("/")
async def root():
    return {"message": "Spam & Phishing Analysis Server is running. Use POST /analyze to analyze messages."}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 3000))
    uvicorn.run(app, host="0.0.0.0", port=port)
