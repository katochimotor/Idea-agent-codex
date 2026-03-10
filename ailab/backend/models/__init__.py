"""SQLModel table declarations for the canonical v2 schema."""

from backend.models.cluster_model import Problem, ProblemCluster, ProblemClusterMembership
from backend.models.document_model import Document, DocumentChunk, DocumentFingerprint
from backend.models.idea_model import Idea, IdeaDetail, IdeaEvidence, IdeaScore, IdeaScoreRecord, Report
from backend.models.job_model import Job, JobEvent
from backend.models.model_registry_model import ModelRegistryEntry, PromptVersion
from backend.models.project_model import Project, ProjectFile
from backend.models.run_model import ExtractionRun, PipelineRun, RunArtifact
from backend.models.source_model import Source, SourceCheckpoint
from backend.models.vector_model import VectorCollection, VectorEntry, VectorSyncRun

__all__ = [
    "Document",
    "DocumentChunk",
    "DocumentFingerprint",
    "ExtractionRun",
    "Idea",
    "IdeaDetail",
    "IdeaEvidence",
    "IdeaScore",
    "IdeaScoreRecord",
    "Job",
    "JobEvent",
    "ModelRegistryEntry",
    "PipelineRun",
    "Problem",
    "ProblemCluster",
    "ProblemClusterMembership",
    "Project",
    "ProjectFile",
    "PromptVersion",
    "Report",
    "RunArtifact",
    "Source",
    "SourceCheckpoint",
    "VectorCollection",
    "VectorEntry",
    "VectorSyncRun",
]
