from fastapi import APIRouter

from backend.agents.runner_agent import RunnerAgent


router = APIRouter(prefix="/sources", tags=["sources"])
runner = RunnerAgent()


@router.get("")
def list_sources():
    return {
        "sources": ["Reddit", "Hacker News", "RSS", "Manual"],
        "available_cli": runner.detect_available_clis(),
    }
