from __future__ import annotations

from datetime import datetime

from sqlmodel import Session, select

from backend.models.job_model import Job, JobEvent


class JobRepository:
    def now(self) -> str:
        return datetime.utcnow().isoformat()

    def create_job(
        self,
        session: Session,
        *,
        job_type: str,
        payload_json: str | None = None,
        requested_by: str | None = None,
        priority: int = 100,
        parent_job_id: int | None = None,
    ) -> Job:
        now = self.now()
        job = Job(
            job_type=job_type,
            status="queued",
            priority=priority,
            requested_by=requested_by,
            parent_job_id=parent_job_id,
            payload_json=payload_json,
            result_json=None,
            error_message=None,
            retry_count=0,
            max_retries=3,
            scheduled_at=now,
            started_at=None,
            finished_at=None,
            created_at=now,
            updated_at=now,
        )
        session.add(job)
        session.flush()
        self.add_event(session, job.id, "job_created", "queued", f"Job {job.job_type} queued")
        session.commit()
        session.refresh(job)
        return job

    def add_event(
        self,
        session: Session,
        job_id: int,
        event_type: str,
        status: str | None,
        message: str,
        payload_json: str | None = None,
    ) -> JobEvent:
        event = JobEvent(
            job_id=job_id,
            event_type=event_type,
            status=status,
            message=message,
            payload_json=payload_json,
            created_at=self.now(),
        )
        session.add(event)
        session.flush()
        return event

    def get_job(self, session: Session, job_id: int) -> Job | None:
        return session.get(Job, job_id)

    def get_events(self, session: Session, job_id: int) -> list[JobEvent]:
        return session.exec(
            select(JobEvent).where(JobEvent.job_id == job_id).order_by(JobEvent.created_at.asc())
        ).all()

    def claim_next_job(self, session: Session) -> Job | None:
        job = session.exec(
            select(Job)
            .where(Job.status.in_(["queued", "retrying"]))
            .order_by(Job.priority.asc(), Job.created_at.asc())
        ).first()
        if not job:
            return None

        now = self.now()
        job.status = "running"
        job.started_at = now
        job.updated_at = now
        self.add_event(session, job.id, "job_claimed", "running", f"Job {job.job_type} started")
        session.commit()
        session.refresh(job)
        return job
