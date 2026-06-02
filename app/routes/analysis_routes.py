from fastapi import APIRouter, Depends

from app.controllers.analysis_controller import analyze, report_phishing
from app.middleware.auth import verify_internal_api_key
from app.models.analysis import AnalysisResponse


router = APIRouter(dependencies=[Depends(verify_internal_api_key)])

router.add_api_route(
    "/analyze",
    analyze,
    methods=["POST"],
    response_model=AnalysisResponse,
)
router.add_api_route("/report", report_phishing, methods=["POST"])
