"""Data models used across the pipeline."""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime


@dataclass
class Record:
    """Represents a single data record from an external source."""
    id: str
    timestamp: datetime
    source: str
    payload: Dict[str, Any]
    tags: List[str] = field(default_factory=list)

    def is_valid(self) -> bool:
        return bool(self.id and self.source and self.payload)

    def age_seconds(self) -> float:
        return (datetime.now() - self.timestamp).total_seconds()


@dataclass
class BatchResult:
    """Result of processing a batch of records."""
    batch_id: str
    total: int
    success: int
    failed: int
    errors: List[str] = field(default_factory=list)
    duration_ms: float = 0.0

    @property
    def success_rate(self) -> float:
        return self.success / self.total if self.total > 0 else 0.0


@dataclass
class PipelineState:
    """Tracks the current state of a pipeline execution."""
    pipeline_name: str
    current_step: int = 0
    total_steps: int = 0
    status: str = "idle"
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    step_results: Dict[str, Any] = field(default_factory=dict)

    def advance(self, step_name: str, result: Any):
        self.current_step += 1
        self.step_results[step_name] = result

    def is_complete(self) -> bool:
        return self.current_step >= self.total_steps
