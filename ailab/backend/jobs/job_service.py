from __future__ import annotations

import json

from sqlmodel import Session

from backend.jobs.job_repository import JobRepository
from backend.models.job_model import Job
from backend.services.pipeline_orchestration_service import PipelineOrchestrationService


class JobService:
    def __init__(self) -> None:
        self.repository = JobRepository()
        self.orchestration = PipelineOrchestrationService()

    def enqueue_job(
        self,
        session: Session,
        *,
        job_type: str,
        payload: dict | None = None,
        requested_by: str | None = None,
        priority: int = 100,
        parent_job_id: int | None = None,
    ) -> Job:
        return self.repository.create_job(
            session,
            job_type=job_type,
            payload_json=json.dumps(payload or {}, ensure_ascii=False),
            requested_by=requested_by,
            priority=priority,
            parent_job_id=parent_job_id,
        )

    def claim_next_job(self, session: Session) -> Job | None:
        return self.repository.claim_next_job(session)

    def get_job(self, session: Session, job_id: int) -> Job | None:
        return self.repository.get_job(session, job_id)

    def get_job_events(self, session: Session, job_id: int) -> list[dict]:
        events = self.repository.get_events(session, job_id)
        return [
            {
                "id": event.id,
                "event_type": event.event_type,
                "status": event.status,
                "message": event.message,
                "payload": json.loads(event.payload_json) if event.payload_json else None,
                "created_at": event.created_at,
            }
            for event in events
        ]

    def execute_job(self, session: Session, job_id: int) -> dict:
        job = self.repository.get_job(session, job_id)
        if not job:
            raise ValueError(f"Job {job_id} not found")

        try:
            result = self.orchestration.execute_job(session, job)
            job.status = "completed"
            job.result_json = json.dumps(result, ensure_ascii=False)
            job.error_message = None
            job.finished_at = self.repository.now()
            job.updated_at = job.finished_at
            self.repository.add_event(session, job.id, "job_completed", "completed", f"Job {job.job_type} completed")
            session.commit()
            return result
        except Exception as exc:
            job.status = "failed"
            job.error_message = str(exc)
            job.finished_at = self.repository.now()
            job.updated_at = job.finished_at
            self.repository.add_event(session, job.id, "job_failed", "failed", str(exc))
            session.commit()
            raise
