from fastapi import HTTPException

from analyze_message import analyze_message
from mongodb_handler import save_phishing_message

from app.models.analysis import AnalysisRequest, ReportRequest


async def analyze(request: AnalysisRequest):
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    try:
        result = analyze_message(request.message)
        print(f"Analysis result for message: {result}")
        if result["final_decision"] == "phishing":
            await save_phishing_message(request.message, result)

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def report_phishing(request: ReportRequest):
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    success = await save_phishing_message(
        request.message,
        {"source": "frontend_report", "metadata": request.metadata},
    )

    if success:
        return {"status": "success", "message": "Phishing message reported and saved."}

    raise HTTPException(status_code=500, detail="Failed to save report to database.")
