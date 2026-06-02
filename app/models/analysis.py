from pydantic import BaseModel


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
