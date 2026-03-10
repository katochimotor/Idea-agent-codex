import json

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from backend.database.db import get_session
from backend.jobs.job_service import JobService


router = APIRouter(prefix="/jobs", tags=["jobs"])
job_service = JobService()


@router.post("/discover")
def enqueue_discover_job(session: Session = Depends(get_session)):
    job = job_service.enqueue_job(
        session,
        job_type="discover_ideas",
        payload={},
        requested_by="dashboard",
        priority=50,
    )
    return {"job_id": job.id, "status": job.status, "job_type": job.job_type}


@router.post("/embeddings/rebuild")
def enqueue_embedding_rebuild(session: Session = Depends(get_session)):
    job = job_service.enqueue_job(
        session,
        job_type="refresh_embeddings",
        payload={},
        requested_by="dashboard",
        priority=80,
    )
    return {"job_id": job.id, "status": job.status, "job_type": job.job_type}


@router.get("/{job_id}")
def get_job(job_id: int, session: Session = Depends(get_session)):
    job = job_service.get_job(session, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return {
        "id": job.id,
        "job_type": job.job_type,
        "status": job.status,
        "result": json.loads(job.result_json) if job.result_json else None,
        "error_message": job.error_message,
        "created_at": job.created_at,
        "started_at": job.started_at,
        "finished_at": job.finished_at,
    }


@router.get("/{job_id}/events")
def get_job_events(job_id: int, session: Session = Depends(get_session)):
    job = job_service.get_job(session, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job_service.get_job_events(session, job_id)
