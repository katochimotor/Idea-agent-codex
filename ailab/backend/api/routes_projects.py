from pydantic import BaseModel
from fastapi import APIRouter, Depends
from sqlmodel import Session

from backend.controllers.project_controller import ProjectController
from backend.database.db import get_session


class CreateProjectRequest(BaseModel):
    idea_id: int
    title: str


router = APIRouter(prefix="/projects", tags=["projects"])
controller = ProjectController()


@router.post("")
def create_project(payload: CreateProjectRequest, session: Session = Depends(get_session)):
    return controller.create_project(session, payload.idea_id, payload.title)
