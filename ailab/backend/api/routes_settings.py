from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from backend.database.db import get_session
from backend.services.provider_settings_service import ProviderSettingsService


class ProviderRequest(BaseModel):
    provider: str
    api_key: str | None = None


router = APIRouter(prefix="/settings", tags=["settings"])
service = ProviderSettingsService()


@router.get("/providers")
def list_provider_settings(session: Session = Depends(get_session)):
    return service.list_settings(session)


@router.post("/providers/test")
def test_provider_connection(payload: ProviderRequest, session: Session = Depends(get_session)):
    try:
        result = service.test_connection(session, payload.provider, payload.api_key)
        if not payload.api_key:
            service.mark_tested(session, payload.provider)
        return result
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/providers/save")
def save_provider_configuration(payload: ProviderRequest, session: Session = Depends(get_session)):
    try:
        saved = service.save_provider(session, payload.provider, payload.api_key)
        service.mark_tested(session, payload.provider)
        return saved
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
