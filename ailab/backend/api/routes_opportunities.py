from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session

from backend.controllers.opportunity_controller import OpportunityController
from backend.database.db import get_session


router = APIRouter(prefix="/opportunities", tags=["opportunities"])
controller = OpportunityController()


@router.get("")
def list_opportunities(limit: int = Query(default=6, ge=1, le=50), session: Session = Depends(get_session)):
    return controller.list_opportunities(session, limit=limit)


@router.get("/{cluster_id}")
def get_opportunity_detail(cluster_id: int, session: Session = Depends(get_session)):
    payload = controller.get_opportunity_detail(session, cluster_id)
    if not payload:
        raise HTTPException(status_code=404, detail="Opportunity cluster not found")
    return payload
