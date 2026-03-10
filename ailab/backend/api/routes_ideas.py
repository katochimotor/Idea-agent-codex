from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from backend.controllers.idea_controller import IdeaController
from backend.database.db import get_session


router = APIRouter(prefix="/ideas", tags=["ideas"])
controller = IdeaController()


@router.get("")
def list_ideas(session: Session = Depends(get_session)):
    return controller.list_ideas(session)


@router.post("/discover")
def discover_ideas(session: Session = Depends(get_session)):
    return controller.discover_ideas(session)


@router.get("/{idea_id}")
def get_idea(idea_id: int, session: Session = Depends(get_session)):
    idea = controller.get_idea(session, idea_id)
    if not idea:
        raise HTTPException(status_code=404, detail="Idea not found")
    return idea
