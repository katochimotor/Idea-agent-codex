from __future__ import annotations

import threading
import time

from sqlmodel import Session

from backend.database.db import engine
from backend.jobs.job_service import JobService
from backend.logger import logger
from backend.settings import settings


class BackgroundJobWorker:
    def __init__(self) -> None:
        self.job_service = JobService()
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run_loop, name="ailab-background-worker", daemon=True)
        self._thread.start()
        logger.info("background worker started")

    def stop(self) -> None:
        self._stop_event.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=3)
        logger.info("background worker stopped")

    def _run_loop(self) -> None:
        while not self._stop_event.is_set():
            job_id: int | None = None
            with Session(engine) as session:
                job = self.job_service.claim_next_job(session)
                if job:
                    job_id = job.id

            if job_id is None:
                time.sleep(settings.worker_poll_interval_seconds)
                continue

            try:
                with Session(engine) as session:
                    self.job_service.execute_job(session, job_id)
            except Exception as exc:
                logger.exception("background job %s failed: %s", job_id, exc)
