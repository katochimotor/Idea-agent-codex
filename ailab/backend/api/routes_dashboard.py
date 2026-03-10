from fastapi import APIRouter

from backend.controllers.analysis_controller import AnalysisController
from backend.controllers.dashboard_controller import DashboardController


router = APIRouter(prefix="/dashboard", tags=["dashboard"])
dashboard_controller = DashboardController()
analysis_controller = AnalysisController()


@router.get("")
def get_dashboard():
    return dashboard_controller.get_dashboard()


@router.get("/analytics")
def get_analytics():
    return analysis_controller.get_summary()
