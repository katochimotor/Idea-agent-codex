from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session

from backend.controllers.idea_controller import IdeaController
from backend.database.db import get_session


router = APIRouter(prefix="/ideas", tags=["ideas"])
controller = IdeaController()


@router.get("")
def list_ideas(
    sort_by: str = Query(default="score", pattern="^(score|date)$"),
    order: str = Query(default="desc", pattern="^(asc|desc)$"),
    topic: str | None = None,
    source: str | None = None,
    search: str | None = None,
    include_archived: bool = False,
    session: Session = Depends(get_session),
):
    return controller.list_ideas(
        session,
        sort_by=sort_by,
        order=order,
        topic=topic,
        source=source,
        search=search,
        include_archived=include_archived,
    )


@router.post("/discover")
def discover_ideas(session: Session = Depends(get_session)):
    return controller.discover_ideas(session)


@router.get("/{idea_id}")
def get_idea(idea_id: int, session: Session = Depends(get_session)):
    idea = controller.get_idea(session, idea_id)
    if not idea:
        raise HTTPException(status_code=404, detail="Idea not found")
    return idea


@router.post("/{idea_id}/archive")
def archive_idea(idea_id: int, session: Session = Depends(get_session)):
    payload = controller.set_status(session, idea_id, "archived")
    if not payload:
        raise HTTPException(status_code=404, detail="Idea not found")
    return payload


@router.post("/{idea_id}/restore")
def restore_idea(idea_id: int, session: Session = Depends(get_session)):
    payload = controller.set_status(session, idea_id, "active")
    if not payload:
        raise HTTPException(status_code=404, detail="Idea not found")
    return payload


@router.post("/{idea_id}/delete")
def delete_idea(idea_id: int, session: Session = Depends(get_session)):
    payload = controller.set_status(session, idea_id, "rejected")
    if not payload:
        raise HTTPException(status_code=404, detail="Idea not found")
    return payload
