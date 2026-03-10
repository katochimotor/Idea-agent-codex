from fastapi import APIRouter, Depends
from sqlmodel import Session

from backend.controllers.analysis_controller import AnalysisController
from backend.controllers.dashboard_controller import DashboardController
from backend.database.db import get_session


router = APIRouter(prefix="/dashboard", tags=["dashboard"])
dashboard_controller = DashboardController()
analysis_controller = AnalysisController()


@router.get("")
def get_dashboard(session: Session = Depends(get_session)):
    return dashboard_controller.get_dashboard(session)


@router.get("/analytics")
def get_analytics(session: Session = Depends(get_session)):
    return analysis_controller.get_summary(session)
